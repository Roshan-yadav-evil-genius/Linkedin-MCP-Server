"""Selector resolver for LinkedIn search-people page (method names mirror profile page resolver)."""
from playwright.async_api import Locator, Page

from core.selector_resolver import SelectorResolver

from .selector_keys import SearchPageKey
from .selector_registry import SEARCH_PAGE_SELECTORS


class LinkedInSearchPageSelectors(SelectorResolver):
    """
    Selector resolver for LinkedIn search results (people).

    Mirrors ``LinkedInProfilePageSelectors`` API; wire real selectors in ``selector_registry``.

    Usage:
        selectors = LinkedInSearchPageSelectors(page)
        connect_btn = selectors.connect_button()

    The get() method is also available for less common selectors:
        selectors.get(SearchPageKey.REMOVE_CONNECTION_BUTTON)
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, SEARCH_PAGE_SELECTORS)

    def all_filters_button(self) -> Locator:
        return self.get(SearchPageKey.ALL_FILTERS_BUTTON)

    def filter_panel(self) -> Locator:
        return self.get(SearchPageKey.FILTER_PANEL)
