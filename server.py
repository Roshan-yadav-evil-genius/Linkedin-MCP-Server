import json
import logging

from fastmcp import FastMCP

from chrome_profile_manager import PageNotFoundError, get_chrome_profile_manager
from page.search_page.action.types import Filter
from utils import html_to_markdown

mcp = FastMCP("LinkedInMCP")
logger = logging.getLogger(__name__)


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
    pass


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
    pass

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
    pass

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
    pass


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
    - Status, summary, or `page_id` guidance string (implementation-defined until wired)

    Notes:
    - This signature does **not** take `page_id`; the implementation is responsible for navigation or session page choice
    - For **facet filters** (degrees, connections of, followers of), open the people search results in a tab with `open_page`, pass that `page_id` to `apply_filters`, and ensure the UI shows the All filters / results view expected by automation
    - Requires an authenticated session for full results (typically after `login`)
    - This tool only drives the browser; it does not return the results body. After the page has updated, call `get_page_content` with the tab’s `page_id` so the agent receives the current view as Markdown
    """
    pass

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
    - Status or result string (implementation-defined)

    Notes:
    - Contrast with `search_people`, which targets broader people search
    - Requires an authenticated session (typically after `login`)
    - Exact navigation (My Network → Connections vs other entry points) is implementation-defined
    - This tool only drives the browser; it does not return the results body. After the page has updated, call `get_page_content` with the tab’s `page_id` so the agent receives the current view as Markdown
    """
    pass

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
    pass

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
    pass

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
    pass


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
