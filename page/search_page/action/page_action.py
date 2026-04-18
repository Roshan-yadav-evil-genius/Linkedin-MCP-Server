from .atomic_action import ClickOnAllFiltersButton, ClickOnPaginationNextButton, ClickOnPaginationPreviousButton
from .molecular_action import ApplyFilters
from .page_utility import SearchPageAction
from .types import Filter
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)


class SearchPage(SearchPageAction):


    async def apply_filters(self, filter: Filter):
        apply_filters = ApplyFilters(self.page, filter)
        await apply_filters.accomplish()
    

    async def click_on_pagination_next_button(self):
        click_on_pagination_next_button = ClickOnPaginationNextButton(self.page)
        await click_on_pagination_next_button.accomplish()
    

    async def click_on_pagination_previous_button(self):
        click_on_pagination_previous_button = ClickOnPaginationPreviousButton(self.page)
        await click_on_pagination_previous_button.accomplish()

