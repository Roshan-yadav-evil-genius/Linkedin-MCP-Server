import asyncio
import logging
import sys
from pathlib import Path

_test_dir = Path(__file__).resolve().parent
_repo_root = _test_dir.parent
sys.path.insert(0, str(_repo_root))

from test.base import configure_logging, persistent_context_kwargs
from page.search_page.action.page_action import SearchPage

configure_logging()
logger = logging.getLogger(__name__)

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(**persistent_context_kwargs())

        page = await context.new_page()
        query = "https://www.linkedin.com/search/results/people/?keywords=arduino&origin=SWITCH_SEARCH_VERTICAL"
        logger.info("Navigating to Search People: %s", query)
        await page.goto(query, wait_until="load")
        search_page_action = SearchPage(page)
        await search_page_action.wait_for_page_to_load()
        await search_page_action.open_filter_panel()
        await context.wait_for_event("close", timeout=0)
        await context.close()


asyncio.run(main())
