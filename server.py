import json
import logging
from urllib.parse import quote_plus, urlparse

from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context

from chrome_profile_manager import ChromeProfileManager
from core.utils import html_to_markdown
from page.messaging_page.action.page_action import MessagingPage
from page.profile_page.actions.page_action import ProfilePage
from page.search_page.action.page_action import SearchPage
from page.search_page.action.types import Filter
from test.base import configure_logging

mcp = FastMCP("LinkedInMCP")

configure_logging()
logger = logging.getLogger(__name__)

browser = ChromeProfileManager()

LINKEDIN_LOGIN_URL = "https://www.linkedin.com/login"


def _is_linkedin_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    hostname = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and "linkedin.com" in hostname


def _linkedin_action_message(tool_name: str, ok: bool) -> str:
    if ok:
        return f"Success: {tool_name} completed."
    return f"Failed: {tool_name} did not complete or verify. Check server logs for details."


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
        logger.exception(
            "_ensure_messaging_thread goto failed session_id=%s", session_id
        )
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
        logger.exception(
            "_ensure_messaging_thread wait failed session_id=%s", session_id
        )
        return f"Messaging page did not become ready in time: {e}", None

    try:
        ok = await messaging.load_chat(normalized)
    except Exception as e:
        logger.exception(
            "_ensure_messaging_thread load_chat failed session_id=%s", session_id
        )
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
    """Open LinkedIn login for manual authentication in this session tab."""
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(LINKEDIN_LOGIN_URL, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_login failed session_id=%s", ctx.session_id)
        return f"Failed to open LinkedIn login page: {e}"
    return "Opened LinkedIn login page. Complete sign-in in the browser tab."


@mcp.tool
async def linkedin_open_page(url: str, ctx: Context = CurrentContext()) -> str:
    """Navigate this session tab to a LinkedIn HTTPS URL."""
    normalized = (url or "").strip()
    if not _is_linkedin_url(normalized):
        return "Failed: url must be a valid https://...linkedin.com/... URL."
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(normalized, wait_until="load")
    except Exception as e:
        logger.exception("linkedin_open_page failed session_id=%s", ctx.session_id)
        return f"Failed to open URL: {e}"
    return f"Opened LinkedIn page: {normalized}"


@mcp.tool
async def linkedin_close_page(ctx: Context = CurrentContext()) -> str:
    """Close only this session's managed tab."""
    status = await browser.close_page(ctx.session_id)
    if status == "closed":
        return "Closed this session tab."
    if status in {"not_found", "already_closed"}:
        return "No open session tab found to close."
    return "Failed to close this session tab. Check server logs for details."


@mcp.tool
async def linkedin_run_javascript(script: str, ctx: Context = CurrentContext()) -> str:
    """Evaluate JavaScript on the current session page and return the result."""
    if not (script or "").strip():
        return "Failed: script must not be empty."
    page = await browser.get_page(ctx.session_id)
    try:
        result = await page.evaluate(script)
    except Exception as e:
        logger.exception("linkedin_run_javascript failed session_id=%s", ctx.session_id)
        return f"Failed to evaluate script: {e}"
    if isinstance(result, (dict, list, tuple, int, float, bool)) or result is None:
        return json.dumps(result)
    return str(result)


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
        logger.exception(
            "linkedin_get_page_content failed session_id=%s", ctx.session_id
        )
        return f"Failed to read page content: {e}"


# ============================================================= [ Profile ] =============================================================
@mcp.tool
async def linkedin_send_connection_request(
    profile_url: str,
    note: str = "",
    withdraw: bool = False,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Send a connection invite, or withdraw a pending invite you already sent.

    Use when:
    - The user wants to connect with this person, or cancel an outbound invite before it is accepted.

    Args:
    - `profile_url`: Their profile URL.
    - `note`: Optional invite message when sending (ignored when `withdraw` is True).
    - `withdraw`: False (default) = send invite; True = withdraw pending invite.

    Needs: logged in. LinkedIn may refuse duplicates, limits, or missing pending invite.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception(
            "linkedin_send_connection_request goto failed session_id=%s", ctx.session_id
        )
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception(
            "linkedin_send_connection_request wait failed session_id=%s", ctx.session_id
        )
        return f"Profile page did not become ready in time: {e}"
    try:
        if withdraw:
            ok = await profile.withdraw_connection_request()
        else:
            ok = await profile.send_connection_request(note=note)
    except Exception as e:
        logger.exception(
            "linkedin_send_connection_request failed session_id=%s", ctx.session_id
        )
        return f"Failed: linkedin_send_connection_request raised: {e}"

    return _linkedin_action_message("linkedin_send_connection_request", ok)


@mcp.tool
async def linkedin_follow_profile(
    profile_url: str,
    unfollow: bool = False,
    ctx: Context = CurrentContext(),
) -> str:
    """
    Follow or unfollow a member’s public posts (without using connection invite).

    Use when:
    - The user wants to follow this person, or stop following them.

    Args:
    - `profile_url`: Their profile URL.
    - `unfollow`: False (default) = follow; True = unfollow.

    Needs: logged in.
    """
    page = await browser.get_page(ctx.session_id)
    try:
        await page.goto(profile_url, wait_until="load")
    except Exception as e:
        logger.exception(
            "linkedin_follow_profile goto failed session_id=%s", ctx.session_id
        )
        return f"Failed to open profile URL: {e}"
    profile = ProfilePage(page)
    if not profile.is_valid_page():
        return "This tab is not a LinkedIn profile URL. Use a valid member profile URL."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception(
            "linkedin_follow_profile wait failed session_id=%s", ctx.session_id
        )
        return f"Profile page did not become ready in time: {e}"
    try:
        if unfollow:
            ok = await profile.unfollow_profile()
        else:
            ok = await profile.follow_profile()
    except Exception as e:
        logger.exception("linkedin_follow_profile failed session_id=%s", ctx.session_id)
        return f"Failed: linkedin_follow_profile raised: {e}"
    return _linkedin_action_message("linkedin_follow_profile", ok)


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
            "linkedin_search_people goto failed query=%r in_my_connections=%s",
            query,
            in_my_connections,
        )
        return f"Failed to open LinkedIn people search: {e}"
    scope = "your connections only" if in_my_connections else "all of LinkedIn"
    return (
        f"Opened people search ({scope}) for query={query!r}. "
        "Call linkedin_get_page_content to read the results."
    )


@mcp.tool
async def linkedin_apply_search_filters(
    filter: Filter, ctx: Context = CurrentContext()
) -> str:
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
        logger.exception(
            "linkedin_apply_search_filters wait failed session_id=%s", ctx.session_id
        )
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.apply_filters(filter)
    except Exception as e:
        logger.exception(
            "linkedin_apply_search_filters failed session_id=%s", ctx.session_id
        )
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
        logger.exception(
            "linkedin_search_next_page wait failed session_id=%s", ctx.session_id
        )
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.click_on_pagination_next_button()
    except Exception as e:
        logger.exception(
            "linkedin_search_next_page failed session_id=%s", ctx.session_id
        )
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
        logger.exception(
            "linkedin_search_previous_page wait failed session_id=%s", ctx.session_id
        )
        return f"Search page did not become ready in time: {e}"
    try:
        ok = await search.click_on_pagination_previous_button()
    except Exception as e:
        logger.exception(
            "linkedin_search_previous_page failed session_id=%s", ctx.session_id
        )
        return f"Failed: linkedin_search_previous_page raised: {e}"
    return _linkedin_action_message("linkedin_search_previous_page", ok)


# ============================================================= [ Messaging ] =============================================================
@mcp.tool
async def linkedin_open_chat_with(
    user_name: str, ctx: Context = CurrentContext()
) -> str:
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
    return (
        f"{status} To send text, use linkedin_send_message_to with the same user_name."
    )


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
        logger.exception(
            "linkedin_send_message_to failed session_id=%s", ctx.session_id
        )
        return f"Failed: linkedin_send_message_to raised: {e}"
    return _linkedin_action_message("linkedin_send_message_to", ok)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=9090)
