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

# ============================================================= [ General Browser Tools ] =============================================================
@mcp.tool
async def login(start_url: str = "about:blank") -> str:
    """
    Launch a visible (non-headless) persistent Chromium session for **manual authentication**.

    Use this when:
    - A target page is **behind login/authentication**
    - Automation fails due to **missing/expired session**
    - Human interaction (OTP, CAPTCHA, SSO) is required

    What it does:
    - Opens a real browser using the persistent profile (cookies will be saved)
    - Optionally navigates to `start_url`
    - Waits until the user **closes the browser window**
    - Saves all session data for future automated steps

    After completion:
    - Subsequent tools (e.g., `open_page`, `run_javascript`) will run with the **authenticated session**

    Parameters:
    - start_url: URL to begin login (default: "about:blank")

    Important:
    - This call **blocks** until the browser is closed
    - No `page_id` is returned
    - Do NOT call other browser tools while this is running
    - Ensure no active pages exist before calling (close them if needed)
    """
    await get_chrome_profile_manager().run_interactive_profile_session(start_url=start_url)
    return "Login session completed. Authenticated state saved and ready for automation."


@mcp.tool
async def open_page(url: str)->str:
    """
    Opens a webpage in a long-lived browser page and returns a `page_id`.

    Use when:
    - You need to run multiple JavaScript operations on the same page
    - You want to preserve page state (DOM/session/cookies) between tool calls

    Parameters:
    - url: Target page URL to open

    Returns:
    - page_id: In-memory identifier required by `get_page_content`, `run_javascript`, `close_page`, and LinkedIn tools that take `page_id`

    Notes:
    - Page IDs are stored in memory only (lost on server restart)
    - Must be called before `run_javascript` or other tools that require `page_id`
    """
    return await get_chrome_profile_manager().open_page(url)

@mcp.tool
async def close_page(page_id: str)->str:
    """
    Closes a page opened by `open_page` and releases its in-memory handle.

    Use when:
    - You are done with a page opened by `open_page`
    - You want to avoid accumulating open tabs/pages

    Parameters:
    - page_id: Identifier returned by `open_page`

    Returns:
    - Status string indicating whether the page was closed or not found
    """
    return await get_chrome_profile_manager().close_page(page_id)

@mcp.tool
async def get_page_content(page_id: str) -> str:
    """
    Extracts and returns the current page content as clean Markdown.

    Use when:
    - You need to read or analyze the visible content of a page
    - You want structured text for LLM processing (instead of raw HTML)

    Parameters:
    - page_id: Identifier returned by `open_page`

    Returns:
    - Markdown string of the page’s visible content

    Notes:
    - Only works on pages opened via `open_page`
    - Reflects the current DOM state (after JS/rendering)
    - Excludes hidden elements, scripts, and styles
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
    Executes JavaScript in the context of a previously opened page and returns the result.

    Use when:
    - You need to interact with the DOM (click, type, extract data, etc.)
    - You want to run custom logic directly inside the page

    Parameters:
    - page_id: Identifier returned by `open_page`
    - script: JavaScript code to execute (must return a value)

    Returns:
    - Result of the executed script (serialized to string)

    Notes:
    - Runs using Playwright `page.evaluate`
    - Has access to the live DOM and browser APIs
    - The script should explicitly `return` a value
    - Fails if `page_id` is invalid or page is closed
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
    Sends a LinkedIn connection request to the member whose profile is loaded in the tab for `page_id`.

    Use when:
    - The user wants to connect with this specific person
    - The visible page is that person’s profile (not search results or feed)

    Parameters:
    - page_id: Tab handle from `open_page`; must already show the target member’s profile URL
    - note: Optional personalized message (empty string means send without a note, if the UI allows)

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - May no-op or error if already connected, invite pending, or LinkedIn limits apply
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
    Withdraws your pending outbound connection request for the member whose profile is loaded in the tab for `page_id`.

    Use when:
    - The user previously sent a request and wants to cancel it before it is accepted
    - The profile shows a pending invitation from you

    Parameters:
    - page_id: Tab handle from `open_page`; must already show that member’s profile

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - Use `send_connection_request` to send a new request, not this tool
    - Fails or no-ops if there is no pending request to withdraw
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
    Follows the member whose profile is loaded in the tab for `page_id` (subscribe to their public updates).

    Use when:
    - The user wants to follow this person without necessarily sending a connection request
    - The visible page is that person’s profile

    Parameters:
    - page_id: Tab handle from `open_page`; must already show the target member’s profile

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - May no-op if already following or if the control is not available
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
    Unfollows the member whose profile is loaded in the tab for `page_id`.

    Use when:
    - The user wants to stop following this person’s updates
    - The visible page is that person’s profile

    Parameters:
    - page_id: Tab handle from `open_page`; must already show the target member’s profile

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - May no-op if not currently following
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
    Runs a LinkedIn **people** search for the given keywords (global search, not limited to your connections list).

    Use when:
    - You need to find candidates by title, company, skills, or other keywords
    - You will refine results later with `apply_filters` on a people-search tab opened via `open_page`

    Parameters:
    - query: Search string as the user would type in LinkedIn people search

    Returns:
    - Message including a new `page_id` for the opened people-search tab (use with `get_page_content` and `apply_filters`)

    Notes:
    - This signature does **not** take `page_id`; it opens a new tracked tab via the same browser session as `open_page`
    - For **facet filters** (degrees, connections of, followers of), open the people search results in a tab with `open_page`, pass that `page_id` to `apply_filters`, and ensure the UI shows the All filters / results view expected by automation
    - Requires an authenticated session for full results (typically after `login`)
    - This tool only drives the browser; it does not return the results body. After the page has updated, call `get_page_content` with the tab’s `page_id` so the agent receives the current view as Markdown
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
    Searches **within your existing LinkedIn connections** (or the product flow that lists “my connections”) for a name or keyword.

    Use when:
    - The user wants to find someone they are already connected to
    - Narrowing to first-degree network, not open LinkedIn-wide people discovery

    Parameters:
    - query: Name or keyword to match within the connections search experience

    Returns:
    - Message including a new `page_id` for the opened tab (1st-degree network filter on people search)

    Notes:
    - Contrast with `search_people`, which targets broader people search
    - Requires an authenticated session (typically after `login`)
    - Exact navigation (My Network → Connections vs other entry points) is implementation-defined
    - This tool only drives the browser; it does not return the results body. After the page has updated, call `get_page_content` with the tab’s `page_id` so the agent receives the current view as Markdown
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
    Opens or uses the LinkedIn **people search** filter UI for the tab `page_id` and applies the structured criteria in `filter` (connection degrees, connections-of, followers-of).

    Use when:
    - The tab already shows LinkedIn **people search results** (or the filter panel for that search)
    - You need to restrict by 1st/2nd/3rd degree, “connections of”, or “followers of” before viewing updated results

    Parameters:
    - page_id: Tab handle from `open_page`; must be on the people search / filters context automation expects
    - filter: Pydantic model with:
        - degree: list of 1, 2, and/or 3 (first-, second-, third-degree); semantics align with LinkedIn’s network filters
        - connection_of: optional full name to restrict to people connected to that member (if supported in UI)
        - followers_of: optional full name to restrict to people who follow that member (if supported in UI)

    Returns:
    - Status or outcome string (implementation-defined); may imply confirming “Show results” in the UI

    Notes:
    - Requires an authenticated session (typically after `login`)
    - Call after the people search page for this `page_id` is ready; often used after `search_people` once a stable tab exists, or after `open_page` to a people search URL
    - Field-level descriptions also live on the `Filter` model in code (`page/search_page/action/types.py`)
    - This tool only mutates the page; it does not return updated results. After filters are applied and the results view has refreshed, call `get_page_content(page_id)` so the agent reads the new state as Markdown
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
    Clicks the **next** control on LinkedIn **people search results** pagination for the tab `page_id`.

    Use when:
    - The user wants the following page of results for the same query and filters
    - More results exist and the next control is visible

    Parameters:
    - page_id: Tab handle from `open_page`; must already show people search results with pagination

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - Does not change the query; only moves within paginated results
    - After the next page loads, call `get_page_content(page_id)` so the agent receives the updated results as Markdown
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
    Clicks the **previous** control on LinkedIn **people search results** pagination for the tab `page_id`.

    Use when:
    - The user wants the prior page of results
    - The previous control is visible

    Parameters:
    - page_id: Tab handle from `open_page`; must already show people search results with pagination

    Returns:
    - Status or outcome string (implementation-defined)

    Notes:
    - Requires an authenticated session (typically after `login`)
    - After the previous page loads, call `get_page_content(page_id)` so the agent receives the updated results as Markdown
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
async def load_messaging_chat(page_id: str, user_name: str) -> str:
    """
    Opens the conversation with a member by name on the LinkedIn messaging tab for ``page_id``.

    Use when:
    - The tab already shows LinkedIn messaging (for example ``/messaging/thread/new/`` or a thread URL)
    - You need to select a recipient from the name search before sending a message

    Parameters:
    - page_id: Tab handle from ``open_page``
    - user_name: Name to type in the messaging recipient search (must match a selectable result)

    Returns:
    - Status string; on success you may call ``send_messaging_message`` on the same ``page_id``

    Notes:
    - Requires an authenticated session (typically after ``login``)
    - Call ``send_messaging_message`` only after this tool succeeds for the same ``page_id``
    """
    if not (user_name or "").strip():
        return "Failed: user_name must not be empty."
    messaging, err = await run_messaging_page(page_id)
    if err:
        set_messaging_chat_loaded(page_id, False)
        return err
    try:
        ok = await messaging.load_chat(user_name.strip())
    except Exception as e:
        logger.exception("load_messaging_chat failed page_id=%s", page_id)
        set_messaging_chat_loaded(page_id, False)
        return f"Failed: load_messaging_chat raised: {e}"
    set_messaging_chat_loaded(page_id, ok)
    return _linkedin_action_message("load_messaging_chat", ok)


@mcp.tool
async def send_messaging_message(page_id: str, message: str) -> str:
    """
    Types and sends a message in the LinkedIn compose box for ``page_id``.

    Use when:
    - ``load_messaging_chat`` has already succeeded for this ``page_id`` and the conversation is open

    Parameters:
    - page_id: Same tab handle used with ``load_messaging_chat``
    - message: Outbound message body (non-empty)

    Returns:
    - Status string

    Notes:
    - If you have not loaded a chat on this tab, the tool returns an error instructing you to call ``load_messaging_chat`` first
    - Requires an authenticated session (typically after ``login``)
    """
    gate_err = require_messaging_chat_loaded(page_id)
    if gate_err:
        return gate_err
    if not (message or "").strip():
        return "Failed: message must not be empty."
    messaging, err = await run_messaging_page(page_id)
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
