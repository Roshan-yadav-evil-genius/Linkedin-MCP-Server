import logging

from playwright.async_api import Page

from .atomic_action import ClickOnPaginationNextButton, ClickOnPaginationPreviousButton
from .molecular_action import ApplyFilters
from .page_utility import SearchPageAction
from .types import Filter

logger = logging.getLogger(__name__)


class SearchPage(SearchPageAction):
    async def apply_filters(self, filter: Filter) -> bool:
        action = ApplyFilters(self.page, filter)
        await action.accomplish()
        if not action.accomplished:
            logger.error("%s failed while applying filters", action.__class__.__name__)
        return action.accomplished

    async def click_on_pagination_next_button(self) -> bool:
        action = ClickOnPaginationNextButton(self.page)
        await action.accomplish()
        if not action.accomplished:
            logger.error("%s failed", action.__class__.__name__)
        return action.accomplished

    async def click_on_pagination_previous_button(self) -> bool:
        action = ClickOnPaginationPreviousButton(self.page)
        await action.accomplish()
        if not action.accomplished:
            logger.error("%s failed", action.__class__.__name__)
        return action.accomplished

