from playwright.async_api import Page
from page.search_page.action.page_utility import SearchMolecularAction
from page.search_page.action.atomic_action import (
    ClickOnAllFiltersButton,
    ClickOnApplyFiltersButton,
    ClickOnConnectionsOfFilterButton,
    ClickOnFollowersOfFilterButton,
    FillConnectionsOfFilterInput,
    FillFollowersOfFilterInput,
    SelectConnectionsOfSuggestionFirstItem,
    SelectFollowersOfSuggestionFirstItem,
    SyncConnectionDegreeFilters,
)
from page.search_page.action.types import Filter


class ApplyFilters(SearchMolecularAction):
    """Open All filters, sync connection degrees, optional connections-of / followers-of, then Show results."""

    def __init__(self, page: Page, filter: Filter):
        super().__init__(page)
        self.chain_of_actions: list = [
            ClickOnAllFiltersButton(page),
            SyncConnectionDegreeFilters(page, list(filter.degree)),
        ]

        if filter.connection_of:
            self.chain_of_actions.append(ClickOnConnectionsOfFilterButton(page))
            self.chain_of_actions.append(FillConnectionsOfFilterInput(page, filter.connection_of))
            self.chain_of_actions.append(SelectConnectionsOfSuggestionFirstItem(page))

        if filter.followers_of:
            self.chain_of_actions.append(ClickOnFollowersOfFilterButton(page))
            self.chain_of_actions.append(FillFollowersOfFilterInput(page, filter.followers_of))
            self.chain_of_actions.append(SelectFollowersOfSuggestionFirstItem(page))

        self.chain_of_actions.append(ClickOnApplyFiltersButton(page))