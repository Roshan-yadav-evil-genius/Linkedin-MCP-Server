import json
import logging
from urllib.parse import quote_plus, urlparse

from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

from browser_profile_config import persistent_context_kwargs
from chrome_profile_manager import ChromeProfileManager
from core.utils import html_to_markdown
from page.messaging_page.action.page_action import MessagingPage
from page.profile_page.actions.page_action import ProfilePage
from page.search_page.action.page_action import SearchPage
from page.search_page.action.types import Filter

mcp = FastMCP("LinkedInMCP")
logger = logging.getLogger(__name__)

browser = ChromeProfileManager(**persistent_context_kwargs())

LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"


def _is_linkedin_https_url(url: str) -> bool:
    """True if url is http(s) and host is linkedin.com or *.linkedin.com."""
    try:
        p = urlparse((url or "").strip())
    except Exception:
        return False
    if p.scheme not in ("http", "https"):
        return False
    host = (p.netloc or "").split(":")[0].lower()
    if not host:
        return False
    return host == "linkedin.com" or host.endswith(".linkedin.com")


def _linkedin_action_message(tool_name: str, ok: bool) -> str:
    if ok:
        return f"Success: {tool_name} completed."
    return f"Failed: {tool_name} did not complete or verify. Check server logs for details."


def _serialize_eval_result(value: object) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except TypeError:
        return str(value)


async def _ensure_messaging_thread(
    ctx: Context, user_name: str
) -> tuple[str | None, MessagingPage | None]:
    """Prepare LinkedIn messaging UI and recipient; used by messaging tools."""
    session_id = ctx.session_id
    normalized = (user_name or "").strip()
    if not normalized:
        return "Failed: user_name must not be empty.", None

    page = await browser.get_page(session_id)
    url = "https://www.linkedin.com/messaging/thread/new/"
    try:
        await page.goto(url, wait_until="load")
    except Exception as e:
        logger.exception("_ensure_messaging_thread goto failed session_id=%s", session_id)
        return f"Failed to open LinkedIn new message page: {e}", None

    messaging = MessagingPage(page)
    if not messaging.is_valid_page():
        return (
            "This tab is not a LinkedIn messaging URL after navigation. "
            "You may call linkedin_close_page to reset this session's tab.",
            None,
        )
    try:
        await messaging.wait_for_page_to_load()
    except Exception as e:
        logger.exception("_ensure_messaging_thread wait failed session_id=%s", session_id)
        return f"Messaging page did not become ready in time: {e}", None

    try:
        ok = await messaging.load_chat(normalized)
    except Exception as e:
        logger.exception("_ensure_messaging_thread load_chat failed session_id=%s", session_id)
        return f"Failed: load_chat raised: {e}", None

    if not ok:
        return (
            "Failed: load_chat did not complete or verify. Check server logs for details.",
            None,
        )

    return None, messaging


# ============================================================= [ Navigation & page read ] =============================================================
@mcp.tool
async def linkedin_login(ctx: Context = CurrentContext()) -> str:
    """
    Open LinkedIn’s login page so the user can sign in in the browser.

    Use when:
    - The session is logged out or LinkedIn asks for password, 2FA, or CAPTCHA.

    After: continue with profile, search, or messaging tools once signed in.
    """
    try:
        page = await browser.get_page(ctx.session_id)
        await page.goto(LINKEDIN_LOGIN_URL, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_login failed session_id=%s", ctx.session_id)
        return f"Failed to open login URL: {e}"
    return "Login page opened. Complete sign-in in the browser, then continue with other tools."


@mcp.tool
async def linkedin_open_page(url: str, ctx: Context = CurrentContext()) -> str:
    """
    Go to a LinkedIn page (profile, search, company, etc.) in the browser for this session.

    Use when:
    - You need a specific LinkedIn URL open before reading it or using another LinkedIn tool.

    Args:
    - `url`: Full https URL whose host is linkedin.com (e.g. https://www.linkedin.com/in/...).

    After: call `linkedin_get_page_content` or a tool that matches that page type.
    """
    if not _is_linkedin_https_url(url):
        return (
            "Failed: url must be a LinkedIn address (https://www.linkedin.com/... or other *.linkedin.com). "
            "Non-LinkedIn pages are not allowed."
        )
    try:
        page = await browser.get_page(ctx.session_id)
        await page.goto(url, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_open_page failed session_id=%s url=%r", ctx.session_id, url)
        return f"Failed to open URL: {e}"
    return f"Opened URL in this session's page: {url!r}."


@mcp.tool
async def linkedin_close_page(ctx: Context = CurrentContext()) -> str:
    """
    Close the browser tab for this session.

    Use when:
    - You are done with the tab or want a fresh tab before the next navigation.
    """
    await browser.close_page(ctx.session_id)
    return "Page closed successfully."


@mcp.tool
async def linkedin_get_page_content(ctx: Context = CurrentContext()) -> str:
    """
    Read the current page as readable text (Markdown-style) for the model.

    Use when:
    - You need to see listings, names, or UI text after search, filters, or opening a profile.

    Needs: browser already showing the page you care about (`linkedin_open_page` or a search tool first).
    """
    try:
        page = await browser.get_page(ctx.session_id)
        content = await page.content()
        return html_to_markdown(content)
    except Exception as e:
        logger.exception("linkedin_get_page_content failed session_id=%s", ctx.session_id)
        return f"Failed to read page content: {e}"


@mcp.tool
async def linkedin_run_javascript(script: str, ctx: Context = CurrentContext()) -> str:
    """
    Run JavaScript in the page and return the script’s result as text. Use only if no dedicated tool fits.

    Use when:
    - You need a one-off read or action not covered by other LinkedIn tools.

    Args:
    - `script`: JavaScript that ends with `return` so there is a value to send back.
    """
    try:
        page = await browser.get_page(ctx.session_id)
        result = await page.evaluate(script)
    except Exception as e:
        logger.exception("linkedin_run_javascript failed session_id=%s", ctx.session_id)
        return f"JavaScript error: {e}"
    return _serialize_eval_result(result)


# ============================================================= [ Profile ] =============================================================
@mcp.tool
async def linkedin_send_connection_request(
    profile_url: str,
    note: str = "",
    ctx: Context = CurrentContext(),
) -> str:
    """
    Send a LinkedIn connection invite to a member.

    Use when:
    - The user wants to connect with this person.

    Args:
    - `profile_url`: Their profile URL.
    - `note`: Optional invite note; empty for no note when allowed.

    Needs: logged in. LinkedIn may refuse duplicates, limits, or pending states.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_send_connection_request goto failed session_id=%s", ctx.session_id)
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_send_connection_request wait failed session_id=%s", ctx.session_id)
        return f"Profile page did not become ready in time: {e}"
    try:
        ok = await profile.send_connection_request(note=note)
    except Exception as e:
        logger.exception("linkedin_send_connection_request failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_send_connection_request raised: {e}"
    return _linkedin_action_message("linkedin_send_connection_request", ok)


@mcp.tool
async def linkedin_withdraw_connection_request(
    profile_url: str,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Withdraw a pending connection invite you sent to this member.

    Use when:
    - The user wants to cancel an outbound invite before it is accepted.

    Args:
    - `profile_url`: Their profile URL.

    Needs: logged in; no pending invite may mean nothing happens.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_withdraw_connection_request goto failed session_id=%s", ctx.session_id)
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_withdraw_connection_request wait failed session_id=%s", ctx.session_id)
        return f"Profile page did not become ready in time: {e}"
    try:
        ok = await profile.withdraw_connection_request()
    except Exception as e:
        logger.exception("linkedin_withdraw_connection_request failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_withdraw_connection_request raised: {e}"
    return _linkedin_action_message("linkedin_withdraw_connection_request", ok)


@mcp.tool
async def linkedin_follow_profile(
    profile_url: str,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Follow a member’s public posts without connecting.

    Use when:
    - The user wants to follow this person.

    Args:
    - `profile_url`: Their profile URL.

    Needs: logged in.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_follow_profile goto failed session_id=%s", ctx.session_id)
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_follow_profile wait failed session_id=%s", ctx.session_id)
        return f"Profile page did not become ready in time: {e}"
    try:
        ok = await profile.follow_profile()
    except Exception as e:
        logger.exception("linkedin_follow_profile failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_follow_profile raised: {e}"
    return _linkedin_action_message("linkedin_follow_profile", ok)


@mcp.tool
async def linkedin_unfollow_profile(
    profile_url: str,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Stop following a member.

    Use when:
    - The user wants to unfollow this person.

    Args:
    - `profile_url`: Their profile URL.

    Needs: logged in.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_unfollow_profile goto failed session_id=%s", ctx.session_id)
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_unfollow_profile wait failed session_id=%s", ctx.session_id)
        return f"Profile page did not become ready in time: {e}"
    try:
        ok = await profile.unfollow_profile()
    except Exception as e:
        logger.exception("linkedin_unfollow_profile failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_unfollow_profile raised: {e}"
    return _linkedin_action_message("linkedin_unfollow_profile", ok)


# ============================================================= [ People search ] =============================================================
@mcp.tool
async def linkedin_search_people(
    query: str,
    in_my_connections: bool = False,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Search LinkedIn for people by keywords (name, title, company, skills, etc.).

    Use when:
    - You need a list of people matching a query.

    Args:
    - `query`: Search words.
    - `in_my_connections`: True = only your 1st-degree connections; False = all of LinkedIn.

    After: `linkedin_get_page_content` to read results; `linkedin_apply_search_filters` to narrow.
    """
    if in_my_connections:
        url = (
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={quote_plus(query)}"
            "&origin=MEMBER_PROFILE_CANNED_SEARCH"
            "&network=%5B%22F%22%5D"
        )
    else:
        url = (
            "https://www.linkedin.com/search/results/people/"
            f"?keywords={quote_plus(query)}&origin=SWITCH_SEARCH_VERTICAL"
        )
    try:
        page = await browser.get_page(ctx.session_id)
        await page.goto(url, wait_until="load")
    except Exception as e:
        logger.exception(
            "linkedin_search_people goto failed query=%r in_my_connections=%s", query, in_my_connections
        )
        return f"Failed to open LinkedIn people search: {e}"
    scope = "your connections only" if in_my_connections else "all of LinkedIn"
    return (
        f"Opened people search ({scope}) for query={query!r}. "
        "Call linkedin_get_page_content to read the results."
    )


@mcp.tool
async def linkedin_apply_search_filters(filter: Filter, ctx: Context = CurrentContext()) -> str:
    """
    Apply filters on a LinkedIn people search results page (degree, school, company, etc.).

    Use when:
    - Results are too broad and you need to narrow the list.

    Args:
    - `filter`: Fields per the tool schema.

    Needs: people search results already open (`linkedin_search_people` or `linkedin_open_page` to a people-search URL). Then `linkedin_get_page_content`.
    """
    page = await browser.get_page(ctx.session_id)
    search = SearchPage(page)
    if not search.is_valid_page():
        return (
            "This tab is not LinkedIn people search (/search/results/people/). "
            "Use linkedin_search_people, linkedin_open_page with a people search URL, or navigate first."
        )
    try:
        await search.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_apply_search_filters wait failed session_id=%s", ctx.session_id)
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.apply_filters(filter)
    except Exception as e:
        logger.exception("linkedin_apply_search_filters failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_apply_search_filters raised: {e}"
    return _linkedin_action_message("linkedin_apply_search_filters", ok)


@mcp.tool
async def linkedin_search_next_page(ctx: Context = CurrentContext()) -> str:
    """
    Go to the next page of LinkedIn people search results.

    Use when:
    - More results exist and you need the following page.

    Needs: people search results visible. Then `linkedin_get_page_content`.
    """
    page = await browser.get_page(ctx.session_id)
    search = SearchPage(page)
    if not search.is_valid_page():
        return (
            "This tab is not LinkedIn people search (/search/results/people/). "
            "Use linkedin_search_people, linkedin_open_page with a people search URL, or navigate first."
        )
    try:
        await search.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_search_next_page wait failed session_id=%s", ctx.session_id)
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.click_on_pagination_next_button()
    except Exception as e:
        logger.exception("linkedin_search_next_page failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_search_next_page raised: {e}"
    return _linkedin_action_message("linkedin_search_next_page", ok)


@mcp.tool
async def linkedin_search_previous_page(ctx: Context = CurrentContext()) -> str:
    """
    Go to the previous page of LinkedIn people search results.

    Use when:
    - You moved forward and need the prior results page.

    Needs: people search with a working previous control. Then `linkedin_get_page_content`.
    """
    page = await browser.get_page(ctx.session_id)
    search = SearchPage(page)
    if not search.is_valid_page():
        return (
            "This tab is not LinkedIn people search (/search/results/people/). "
            "Use linkedin_search_people, linkedin_open_page with a people search URL, or navigate first."
        )
    try:
        await search.wait_for_page_to_load()
    except Exception as e:
        logger.exception("linkedin_search_previous_page wait failed session_id=%s", ctx.session_id)
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.click_on_pagination_previous_button()
    except Exception as e:
        logger.exception("linkedin_search_previous_page failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_search_previous_page raised: {e}"
    return _linkedin_action_message("linkedin_search_previous_page", ok)


# ============================================================= [ Messaging ] =============================================================
@mcp.tool
async def linkedin_open_chat_with(user_name: str, ctx: Context = CurrentContext()) -> str:
    """
    Open a LinkedIn chat with someone by name (does not send a message).

    Use when:
    - You want to confirm the thread opens before typing.

    Args:
    - `user_name`: Name as shown in LinkedIn’s recipient picker.

    For sending in one step, use `linkedin_send_message_to`. Needs: logged in.
    """
    err, _ = await _ensure_messaging_thread(ctx, user_name)
    if err:
        return err
    status = _linkedin_action_message("linkedin_open_chat_with", True)
    return f"{status} To send text, use linkedin_send_message_to with the same user_name."


@mcp.tool
async def linkedin_send_message_to(
    user_name: str,
    message: str,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Send a LinkedIn direct message to someone chosen by recipient name.

    Use when:
    - The user wants to DM this person.

    Args:
    - `user_name`: Name as in LinkedIn’s new-message recipient search.
    - `message`: Body text (cannot be empty).

    Needs: logged in. Call again for another message if needed.
    """
    if not (message or "").strip():
        return "Failed: message must not be empty."

    err, messaging = await _ensure_messaging_thread(ctx, user_name)
    if err:
        return err
    try:
        ok = await messaging.send_message(message.strip())
    except Exception as e:
        logger.exception("linkedin_send_message_to failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_send_message_to raised: {e}"
    return _linkedin_action_message("linkedin_send_message_to", ok)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
