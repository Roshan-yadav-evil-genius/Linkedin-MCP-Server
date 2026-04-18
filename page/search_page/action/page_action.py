from .atomic_action import ClickOnAllFiltersButton
from .page_utility import SearchPageAction
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)


class SearchPage(SearchPageAction):

    async def open_filter_panel(self):
        click_on_all_filters_button = ClickOnAllFiltersButton(self.page)
        result = await click_on_all_filters_button.accomplish()
        if result.accomplished:
            logger.info("All filters button clicked successfully")
        else:
            logger.error("All filters button clicked failed")
