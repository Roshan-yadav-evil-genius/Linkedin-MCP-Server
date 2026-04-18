"""Search-people page: shared utilities for selectors, validation, waits, and step bases."""
import logging

from core.actions import BaseAtomicAction, BaseMolecularAction, BasePageAction
from playwright.async_api import Page

from ..selectors.selector_resolver import LinkedInSearchPageSelectors

logger = logging.getLogger(__name__)


class PageUtility:
    """Wires search selectors, URL validation, and load wait."""

    def __init__(self, page: Page, **kwargs) -> None:
        super().__init__(page, **kwargs)
        self.search_result = LinkedInSearchPageSelectors(self.page)
        self.search_query = page.url

    def is_valid_page(self) -> bool:
        return "/search/results/people/" in self.search_query

    async def wait_for_page_to_load(self) -> None:
        await self.search_result.all_filters_button().wait_for(state="visible", timeout=20000)
        logger.info("Search page loaded successfully")


class SearchPageAction(PageUtility, BasePageAction):
    """Combines PageUtility with BasePageAction; subclass as SearchPage for orchestration APIs."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)


class SearchAtomicAction(PageUtility, BaseAtomicAction):
    def __init__(self, page: Page) -> None:
        super().__init__(page)


class SearchMolecularAction(PageUtility, BaseMolecularAction):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
