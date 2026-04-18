from core.actions import PageAction
from .atomic_action import ClickOnAllFiltersButton
from .base_action import LinkedInSearchPageMixin
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)

class SearchPageAction(LinkedInSearchPageMixin, PageAction):
    def __init__(self, page: Page):
        super().__init__(page)
        self.search_query = self.page.url
        if not "/search/results/people/" in self.search_query:
            raise ValueError("Invalid LinkedIn search query.")

    def is_valid_page(self) -> bool:
        return "/search/results/people/" in self.search_query
    

    async def wait_for_page_to_load(self):
        await self._wait_for_page_to_load()
        logger.info("Search page loaded successfully")

    async def open_filter_panel(self):
        click_on_all_filters_button = ClickOnAllFiltersButton(self.page)
        result =  await click_on_all_filters_button.accomplish()
        if result.accomplished:
            logger.info("All filters button clicked successfully")
        else:
            logger.error("All filters button clicked failed")