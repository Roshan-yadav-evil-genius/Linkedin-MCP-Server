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
    
    def connections_of_filter_button(self) -> Locator:
        return self.get(SearchPageKey.CONNECTIONS_OF_FILTER_BUTTON)

    def connections_of_filter_input(self) -> Locator:
        return self.get(SearchPageKey.CONNECTIONS_OF_FILTER_INPUT)

    def filter_panel(self) -> Locator:
        return self.get(SearchPageKey.FILTER_PANEL)

    def suggestion_floating_portal_first_item(self) -> Locator:
        return self.get(SearchPageKey.SUGGESTION_FLOATING_PORTAL_ITEM)

    def selected_suggestion_floating_portal_item(self) -> Locator:
        return self.get(SearchPageKey.SELECTED_SUGGESTION_FLOATING_PORTAL_ITEM)

    def followers_of_filter_button(self) -> Locator:
        return self.get(SearchPageKey.FOLLOWERS_OF_FILTER_BUTTON)
    
    def followers_of_filter_input(self) -> Locator:
        return self.get(SearchPageKey.FOLLOWERS_OF_FILTER_INPUT)
    
    def apply_filters_button(self) -> Locator:
        return self.get(SearchPageKey.APPLY_FILTERS_BUTTON)

    def pagination_next_button(self) -> Locator:
        return self.get(SearchPageKey.PAGINATION_NEXT_BUTTON)

    def pagination_current_page(self) -> Locator:
        return self.get(SearchPageKey.PAGINATION_CURRENT_PAGE)
    
    def pagination_previous_button(self) -> Locator:
        return self.get(SearchPageKey.PAGINATION_PREVIOUS_BUTTON)