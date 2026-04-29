import logging
import sys
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.server.context import Context
from fastmcp.utilities.types import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chrome_profile_manager import ChromeProfileManager
from browser_profile_config import persistent_context_kwargs

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


mcp = FastMCP("BrowserMCP")

browser_config = persistent_context_kwargs()
browser = ChromeProfileManager(**browser_config)


@mcp.tool
async def navigate_to_url(url: str,ctx: Context = CurrentContext()) -> str:
    """
    Navigates to the given URL in the browser.
    """
    page_instance = await browser.get_page(ctx.session_id)
    try:
        await page_instance.goto(url,wait_until="load")
    except TimeoutError as e:
        logger.error(f"TimeoutError navigating to URL {url}: {e}")
        return f"Loading timed out, the page is still loading and the desired load state was not reached."

    return "Page navigated to URL successfully"

@mcp.tool
async def page_evaluate(script: str,ctx: Context = CurrentContext()) -> str:
    """
    Evaluates the given script in the current page and returns the result.
    """
    page_instance = await browser.get_page(ctx.session_id)
    result = await page_instance.evaluate(script)
    return str(result)

@mcp.tool
async def get_page_screenshot(ctx: Context = CurrentContext()) -> Image:
    """
    Takes a screenshot of the current page.
    """
    page_instance = await browser.get_page(ctx.session_id)
    screenshot = await page_instance.screenshot()
    return Image(data=screenshot)

@mcp.tool
async def close_page(ctx: Context = CurrentContext()) -> str:
    """
    Closes the current page.
    """
    await browser.close_page(ctx.session_id)
    return "Page closed successfully"

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8878)