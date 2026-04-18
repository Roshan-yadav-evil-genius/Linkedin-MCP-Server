import asyncio
import logging
import sys
from pathlib import Path

_test_dir = Path(__file__).resolve().parent
_repo_root = _test_dir.parent
sys.path.insert(0, str(_repo_root))

from test.base import configure_logging, persistent_context_kwargs
from page.search_page.action.page_action import SearchPage
from page.search_page.action.atomic_action import ClickOnAllFiltersButton, ClickOnConnectionsOfFilterButton, FillConnectionsOfFilterInput, SelectSuggestionFloatingPortalFirstItem
from core.human_behavior import human_wait, DelayConfig

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
        # import atomic actions
        click_on_all_filters_button = ClickOnAllFiltersButton(page)
        result = await click_on_all_filters_button.accomplish()
        if result.accomplished:
            logger.info("All filters button clicked successfully")
        else:
            logger.error("All filters button clicked failed")

        await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        click_on_connections_of_filter_button = ClickOnConnectionsOfFilterButton(page)
        result = await click_on_connections_of_filter_button.accomplish()
        if result.accomplished:
            logger.info("Connections of filter button clicked successfully")
        else:
            logger.error("Connections of filter button clicked failed")

        await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        fill_connections_of_filter_input = FillConnectionsOfFilterInput(page, "Roshan")
        result = await fill_connections_of_filter_input.accomplish()
        if result.accomplished:
            logger.info("Connections of filter input filled successfully")
        else:
            logger.error("Connections of filter input filled failed")

        await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        select_suggestion_floating_portal_first_item = SelectSuggestionFloatingPortalFirstItem(page)
        result = await select_suggestion_floating_portal_first_item.accomplish()
        if result.accomplished:
            logger.info("Suggestion floating portal first item selected successfully")
        else:
            logger.error("Suggestion floating portal first item selected failed")
        await context.wait_for_event("close", timeout=0)
        await context.close()


asyncio.run(main())
