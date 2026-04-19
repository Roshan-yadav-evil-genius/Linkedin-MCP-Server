import json
import logging
from urllib.parse import quote_plus

from fastmcp import FastMCP

from chrome_profile_manager import PageNotFoundError, get_chrome_profile_manager
from linkedin_mcp_bridge import (
    require_messaging_chat_loaded,
    run_messaging_page,
    run_profile_page,
    run_search_page,
    set_messaging_chat_loaded,
)
from page.search_page.action.types import Filter
from utils import html_to_markdown

mcp = FastMCP("LinkedInMCP")
logger = logging.getLogger(__name__)


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

# Agent-facing tool docstrings: one-line summary, when to use (bullets), requirements,
# then outcome / next step. Say "get_page_content" when the agent should read the tab.
# ============================================================= [ General Browser Tools ] =============================================================
@mcp.tool
async def login(start_url: str = "about:blank") -> str:
    """
    Opens a real browser window so a human can sign in (or refresh a LinkedIn session); when they
    close the window, cookies and session data are saved for later tool calls.

    When to use:
    - LinkedIn needs a password, 2FA, CAPTCHA, SSO, or similar and automated steps are not signed in.
    - Session looks expired and other tools fail until someone logs in again.

    Requirements:
    - Close extra automated tabs first if your setup needs a clean slate.
    - Optional `start_url` (default `about:blank`) is where the window first loads.

    Blocking: waits until the browser window is closed; do not run other tools in parallel. No
    `page_id` is returned. Afterward use `open_page` or LinkedIn tools as usual.
    """
    await get_chrome_profile_manager().run_interactive_profile_session(start_url=start_url)
    return "Login session completed. Authenticated state saved and ready for automation."


@mcp.tool
async def open_page(url: str)->str:
    """
    Opens a URL in the managed browser and returns a `page_id` for that tab.

    When to use:
    - You need a stable tab to read with `get_page_content`, run `run_javascript`, or pass into a LinkedIn tool that requires `page_id`.

    Requirements:
    - Working browser profile; use `login` when LinkedIn still needs a human sign-in.

    Next: keep the returned `page_id` until you call `close_page` or the server restarts (ids are in-memory only).
    """
    return await get_chrome_profile_manager().open_page(url)

@mcp.tool
async def close_page(page_id: str)->str:
    """
    Closes the browser tab for `page_id` and removes the server’s handle.

    When to use:
    - The tab is finished or you want to avoid too many open tabs.

    Requirements:
    - `page_id` from `open_page`, `search_people`, `search_person_in_my_connections`, or `open_chat_window_of`.

    Returns a short message (closed, or unknown/closed id).
    """
    return await get_chrome_profile_manager().close_page(page_id)

@mcp.tool
async def get_page_content(page_id: str) -> str:
    """
    Returns what is visibly on the page as Markdown (names, headlines, search rows, etc.).

    When to use:
    - After navigation, search, filters, pagination, or any time you need to see the current screen.

    Requirements:
    - `page_id` for an open tab from `open_page` or a tool that opens a new tab.

    If the id is invalid you get an error string; otherwise you get readable Markdown (noise like scripts and hidden bits is dropped).
    """
    manager = get_chrome_profile_manager()
    try:
        page = manager.get_page(page_id)
    except PageNotFoundError:
        return f"Unknown or closed page_id: {page_id!r}."
    try:
        content = await page.content()
        return html_to_markdown(content)
    except Exception as e:
        logger.exception("get_page_content failed for page_id=%s", page_id)
        return f"Failed to read page content: {e}"

@mcp.tool
async def run_javascript(page_id: str, script: str) -> str:
    """
    Runs your script inside the open tab and returns its result as text (escape hatch when no dedicated tool fits).

    When to use:
    - A one-off click, read, or small automation is needed and there is no named LinkedIn tool for it.

    Requirements:
    - Valid `page_id`. The script must `return` a value so the tool has something to send back.

    Prefer the built-in LinkedIn tools when they match the task. Errors look like `JavaScript error: ...` or an unknown `page_id` message.
    """
    manager = get_chrome_profile_manager()
    try:
        page = manager.get_page(page_id)
    except PageNotFoundError:
        return f"Unknown or closed page_id: {page_id!r}."
    try:
        result = await page.evaluate(script)
    except Exception as e:
        logger.exception("run_javascript failed for page_id=%s", page_id)
        return f"JavaScript error: {e}"
    return _serialize_eval_result(result)

# ============================================================= [ LinkedIn Specific Tools ] =============================================================



# ============================================================= [ Profile Page Tools ] =============================================================
@mcp.tool
async def send_connection_request(page_id: str, note: str = "")->str:
    """
    Sends a connection invite to the person whose LinkedIn profile is open on `page_id`.

    When to use:
    - The user wants to connect with this person and their profile page is already loaded.

    Requirements:
    - Tab must be that member’s profile URL (use `open_page` on their profile first). Signed-in session.
    - LinkedIn may refuse if you are already connected, a request is pending, or limits apply.

    Reply text is `Success: send_connection_request completed.` or `Failed: send_connection_request did not complete or verify. ...`.
    Use an empty `note` to try sending without a message when the site allows it.
    """
    profile, err = await run_profile_page(page_id)
    if err:
        return err
    try:
        ok = await profile.send_connection_request(note=note)
    except Exception as e:
        logger.exception("send_connection_request failed page_id=%s", page_id)
        return f"Failed: send_connection_request raised: {e}"
    return _linkedin_action_message("send_connection_request", ok)


@mcp.tool
async def withdraw_connection_request(page_id: str)->str:
    """
    Withdraws your pending connection request to the person whose profile is open on `page_id`.

    When to use:
    - The user wants to cancel an outbound invite before it is accepted.

    Requirements:
    - Profile URL on that tab; signed in. No pending invite means the action may fail or do nothing.

    Reply uses `Success: withdraw_connection_request completed.` or the matching `Failed: ...` line. To invite again later, use `send_connection_request`.
    """
    profile, err = await run_profile_page(page_id)
    if err:
        return err
    try:
        ok = await profile.withdraw_connection_request()
    except Exception as e:
        logger.exception("withdraw_connection_request failed page_id=%s", page_id)
        return f"Failed: withdraw_connection_request raised: {e}"
    return _linkedin_action_message("withdraw_connection_request", ok)

@mcp.tool
async def follow_profile(page_id: str)->str:
    """
    Follows the person so you see their public updates, without requiring a connection.

    When to use:
    - The user wants to follow this member from their profile page.

    Requirements:
    - Their profile URL on `page_id`; signed in. Already following or missing controls can make this a no-op or failure.

    Reply uses `Success: follow_profile completed.` or `Failed: follow_profile ...`.
    """
    profile, err = await run_profile_page(page_id)
    if err:
        return err
    try:
        ok = await profile.follow_profile()
    except Exception as e:
        logger.exception("follow_profile failed page_id=%s", page_id)
        return f"Failed: follow_profile raised: {e}"
    return _linkedin_action_message("follow_profile", ok)

@mcp.tool
async def unfollow_profile(page_id: str)->str:
    """
    Stops following the person whose profile is open on `page_id`.

    When to use:
    - The user no longer wants this member’s updates in their feed from this action.

    Requirements:
    - Profile URL on that tab; signed in. Not following them can mean a no-op or failure.

    Reply uses `Success: unfollow_profile completed.` or `Failed: unfollow_profile ...`.
    """
    profile, err = await run_profile_page(page_id)
    if err:
        return err
    try:
        ok = await profile.unfollow_profile()
    except Exception as e:
        logger.exception("unfollow_profile failed page_id=%s", page_id)
        return f"Failed: unfollow_profile raised: {e}"
    return _linkedin_action_message("unfollow_profile", ok)


# ============================================================= [ Search Page Tools ] =============================================================
@mcp.tool
async def search_people(query: str)->str:
    """
    Opens LinkedIn people search for keywords across the whole network (not limited to people you already know).

    When to use:
    - Finding candidates by title, company, skills, or other search words.

    Requirements:
    - Signed in for full results.

    Opens a new tab and returns text that includes a fresh `page_id`. Save it, then call `get_page_content` to read who appears. Use `apply_filters` on that same `page_id` when you need degree or “connections of / followers of” style filters.
    """
    url = (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={quote_plus(query)}&origin=SWITCH_SEARCH_VERTICAL"
    )
    try:
        page_id = await get_chrome_profile_manager().open_page(url)
    except Exception as e:
        logger.exception("search_people open_page failed query=%r", query)
        return f"Failed to open LinkedIn people search: {e}"
    return (
        f"Opened LinkedIn people search for query={query!r}. page_id={page_id!r}. "
        "Call get_page_content with this page_id to read the results as Markdown."
    )

@mcp.tool
async def search_person_in_my_connections(query: str)->str:
    """
    Opens people search narrowed to your first-degree network so you can find someone you are already connected to.

    When to use:
    - The user is looking up a connection by name or keyword, not doing a broad talent search.

    Requirements:
    - Signed in.

    Contrast: `search_people` is the wide search; this one is scoped to direct connections. Returns a new `page_id` in the message—call `get_page_content` on it to read the list.
    """
    # https://www.linkedin.com/search/results/people/?keywords=hr&origin=GLOBAL_SEARCH_HEADER&network=%5B%22F%22%5D
    # First-degree network facet on people search (approximates “my connections” discovery).
    url = (
        "https://www.linkedin.com/search/results/people/"
        f"?keywords={quote_plus(query)}"
        "&origin=MEMBER_PROFILE_CANNED_SEARCH"
        "&network=%5B%22F%22%5D"
    )
    try:
        page_id = await get_chrome_profile_manager().open_page(url)
    except Exception as e:
        logger.exception("search_person_in_my_connections open_page failed query=%r", query)
        return f"Failed to open LinkedIn connections-scoped search: {e}"
    return (
        f"Opened LinkedIn people search (1st-degree / connections network) for query={query!r}. "
        f"page_id={page_id!r}. Call get_page_content with this page_id to read the results as Markdown."
    )

@mcp.tool
async def apply_filters(page_id: str, filter: Filter)->str:
    """
    Applies people-search filters on the tab that already shows LinkedIn people search (degrees, connections of, followers of).

    When to use:
    - You have a people results tab and need to narrow who appears before reading or paging.

    Requirements:
    - `page_id` must be people search (for example from `search_people` or `open_page` to a people-search URL). Signed in.
    - Build `filter` from the schema: each field has a short description there.

    Does not return the result list. After the tool responds, call `get_page_content` with the same `page_id`. Reply text follows `Success: apply_filters completed.` or `Failed: apply_filters ...`.
    """
    search, err = await run_search_page(page_id)
    if err:
        return err
    try:
        ok = await search.apply_filters(filter)
    except Exception as e:
        logger.exception("apply_filters failed page_id=%s", page_id)
        return f"Failed: apply_filters raised: {e}"
    return _linkedin_action_message("apply_filters", ok)

@mcp.tool
async def click_on_pagination_next_button(page_id: str)->str:
    """
    Goes to the next page of LinkedIn people search results for the same query and filters.

    When to use:
    - More results exist and you need the following page.

    Requirements:
    - `page_id` on people search with pagination showing; signed in.

    Does not change the search words—only the page index. Then call `get_page_content` to read the new screen. Reply uses `Success: click_on_pagination_next_button completed.` or `Failed: ...`.
    """
    search, err = await run_search_page(page_id)
    if err:
        return err
    try:
        ok = await search.click_on_pagination_next_button()
    except Exception as e:
        logger.exception("click_on_pagination_next_button failed page_id=%s", page_id)
        return f"Failed: click_on_pagination_next_button raised: {e}"
    return _linkedin_action_message("click_on_pagination_next_button", ok)

@mcp.tool
async def click_on_pagination_previous_button(page_id: str)->str:
    """
    Goes back one page in LinkedIn people search results.

    When to use:
    - You moved forward with `click_on_pagination_next_button` and need the prior results page.

    Requirements:
    - People search tab with a visible previous control; signed in.

    Then call `get_page_content` to read the list. Reply uses `Success: click_on_pagination_previous_button completed.` or `Failed: ...`.
    """
    search, err = await run_search_page(page_id)
    if err:
        return err
    try:
        ok = await search.click_on_pagination_previous_button()
    except Exception as e:
        logger.exception("click_on_pagination_previous_button failed page_id=%s", page_id)
        return f"Failed: click_on_pagination_previous_button raised: {e}"
    return _linkedin_action_message("click_on_pagination_previous_button", ok)

# ============================================================= [ Messaging Page Tools ] =============================================================


@mcp.tool
async def open_chat_window_of(user_name: str) -> str:
    """
    Run this before `send_messaging_message` for a new recipient: opens a new messaging tab, picks the person by name, and tells the server this tab is allowed to send.

    Ordering and reuse:
    - Call once when starting (or deliberately switching) a recipient. Reuse the returned `page_id` for every later message to the same person—do not call this again before each send.
    - `user_name` must be non-empty and should match someone you can select from LinkedIn’s recipient search.

    When to use:
    - You need a `page_id` that is cleared for messaging to that person.

    Requirements:
    - Signed in. This tool opens a new tab; it does not take an existing `page_id`.

    The response includes `page_id` on success; pass that same id into `send_messaging_message` one or many times. Call again only for another tab or another recipient.
    """
    if not (user_name or "").strip():
        return "Failed: user_name must not be empty."
    url = "https://www.linkedin.com/messaging/thread/new/"
    try:
        page_id = await get_chrome_profile_manager().open_page(url)
    except Exception as e:
        logger.exception("open_chat_window_of open_page failed user_name=%r", user_name)
        return f"Failed to open LinkedIn new message page: {e}"
    messaging, err = await run_messaging_page(page_id)
    if err:
        set_messaging_chat_loaded(page_id, False)
        return f"{err} page_id={page_id!r}. You may close this tab with close_page if it is not useful."
    try:
        ok = await messaging.load_chat(user_name.strip())
    except Exception as e:
        logger.exception("open_chat_window_of failed page_id=%s", page_id)
        set_messaging_chat_loaded(page_id, False)
        return (
            f"Failed: open_chat_window_of raised: {e} page_id={page_id!r}. "
            "You may close this tab with close_page if it is not useful."
        )
    set_messaging_chat_loaded(page_id, ok)
    status = _linkedin_action_message("open_chat_window_of", ok)
    if ok:
        return (
            f"{status} page_id={page_id!r}. "
            "Use send_messaging_message with this page_id to send one or more messages without calling open_chat_window_of again."
        )
    return f"{status} page_id={page_id!r}."


@mcp.tool
async def send_messaging_message(page_id: str, message: str) -> str:
    """
    Sends one outbound message in the compose box for a tab that `open_chat_window_of` already succeeded on.

    Ordering (read first):
    - If you see “No chat loaded for this tab…”, run `open_chat_window_of` once, then send using the `page_id` it returned.
    - Send the first line and every follow-up by calling this tool again with the same `page_id`; do not reopen the chat between sends.

    When to use:
    - Any message in that loaded thread, including the very first line after the chat is open.

    Requirements:
    - Signed in. `message` must contain real text (whitespace-only is rejected).

    Reply uses `Success: send_messaging_message completed.` or `Failed: send_messaging_message ...`. It does not reopen or reset the thread UI.
    """
    gate_err = require_messaging_chat_loaded(page_id)
    if gate_err:
        return gate_err
    if not (message or "").strip():
        return "Failed: message must not be empty."
    messaging, err = await run_messaging_page(page_id, wait_for_ready=False)
    if err:
        return err
    try:
        ok = await messaging.send_message(message.strip())
    except Exception as e:
        logger.exception("send_messaging_message failed page_id=%s", page_id)
        return f"Failed: send_messaging_message raised: {e}"
    return _linkedin_action_message("send_messaging_message", ok)


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
