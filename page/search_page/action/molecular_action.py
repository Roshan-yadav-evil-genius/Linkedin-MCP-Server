from playwright.async_api import Page
from page.search_page.action.page_utility import SearchMolecularAction
from page.search_page.action.atomic_action import ClickOnAllFiltersButton, ClickOnConnectionsOfFilterButton, ClickOnFollowersOfFilterButton, FillConnectionsOfFilterInput, FillFollowersOfFilterInput, ClickOnApplyFiltersButton, SelectConnectionsOfSuggestionFirstItem, SelectFollowersOfSuggestionFirstItem
from page.search_page.action.types import Filter





class ApplyFilters(SearchMolecularAction):
    def __init__(self, page: Page, filter: Filter):
        super().__init__(page)
        self.chain_of_actions=[]

        if filter.connection_of:
            self.chain_of_actions.append(ClickOnConnectionsOfFilterButton(page))
            self.chain_of_actions.append(FillConnectionsOfFilterInput(page, filter.connection_of))
            self.chain_of_actions.append(SelectConnectionsOfSuggestionFirstItem(page))
        
        if filter.followers_of:
            self.chain_of_actions.append(ClickOnFollowersOfFilterButton(page))
            self.chain_of_actions.append(FillFollowersOfFilterInput(page, filter.followers_of))
            self.chain_of_actions.append(SelectFollowersOfSuggestionFirstItem(page))
        
        if self.chain_of_actions:
            self.chain_of_actions.insert(0, ClickOnAllFiltersButton(page))

        if len(self.chain_of_actions) > 0:
            self.chain_of_actions.append(ClickOnApplyFiltersButton(page))