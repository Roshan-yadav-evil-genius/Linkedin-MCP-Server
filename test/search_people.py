import asyncio
import logging
import sys
from pathlib import Path

_test_dir = Path(__file__).resolve().parent
_repo_root = _test_dir.parent
sys.path.insert(0, str(_repo_root))

from test.base import configure_logging, persistent_context_kwargs
from page.search_page.action.page_action import SearchPage
from page.search_page.action.atomic_action import ClickOnAllFiltersButton, ClickOnConnectionsOfFilterButton, ClickOnPaginationNextButton, ClickOnPaginationPreviousButton, FillConnectionsOfFilterInput, SelectSuggestionFloatingPortalFirstItem, ClickOnFollowersOfFilterButton, FillFollowersOfFilterInput, ClickOnApplyFiltersButton
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
        # click_on_all_filters_button = ClickOnAllFiltersButton(page)
        # await click_on_all_filters_button.accomplish()

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # click_on_connections_of_filter_button = ClickOnConnectionsOfFilterButton(page)
        # await click_on_connections_of_filter_button.accomplish()

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # fill_connections_of_filter_input = FillConnectionsOfFilterInput(page, "Roshan")
        # await fill_connections_of_filter_input.accomplish()

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # click_on_followers_of_filter_button = ClickOnFollowersOfFilterButton(page)
        # await click_on_followers_of_filter_button.accomplish()

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # fill_followers_of_filter_input = FillFollowersOfFilterInput(page, "Roshan")
        # await fill_followers_of_filter_input.accomplish()   

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # select_suggestion_floating_portal_first_item = SelectSuggestionFloatingPortalFirstItem(page)
        # await select_suggestion_floating_portal_first_item.accomplish()

        # await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        # click_on_apply_filters_button = ClickOnApplyFiltersButton(page)
        # await click_on_apply_filters_button.accomplish()

        await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        click_on_pagination_next_button = ClickOnPaginationNextButton(page)
        await click_on_pagination_next_button.accomplish()

        await human_wait(page, config=DelayConfig(min_ms=500, max_ms=1000))
        click_on_pagination_previous_button = ClickOnPaginationPreviousButton(page)
        await click_on_pagination_previous_button.accomplish()

        await context.wait_for_event("close", timeout=0)
        await context.close()


asyncio.run(main())
