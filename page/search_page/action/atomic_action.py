from .page_utility import SearchAtomicAction
from core.human_behavior import human_typing, DelayConfig
from playwright.async_api import Page

class ClickOnAllFiltersButton(SearchAtomicAction):

    async def perform_action(self):
        if await self.search_result.all_filters_button().is_visible():
            await self.search_result.all_filters_button().click()
            await self.search_result.filter_panel().wait_for(state="visible")
            

    async def verify_action(self) -> bool:
        if await self.search_result.filter_panel().is_visible():
            return True
        return False

class ClickOnConnectionsOfFilterButton(SearchAtomicAction):

    async def perform_action(self):
        if await self.search_result.connections_of_filter_button().is_visible():
            await self.search_result.connections_of_filter_button().click()
            await self.search_result.connections_of_filter_input().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.search_result.connections_of_filter_input().is_visible():
            return True
        return False

class FillConnectionsOfFilterInput(SearchAtomicAction):
    def __init__(self, page: Page, connection_name: str):
        super().__init__(page)
        self.connection_name = connection_name

    async def perform_action(self):
        if await self.search_result.connections_of_filter_input().is_visible():
            await human_typing(
                self.search_result.connections_of_filter_input(),
                self.connection_name,
                config=DelayConfig(min_ms=50, max_ms=300),
            )
            await self.search_result.suggestion_floating_portal_first_item().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.search_result.suggestion_floating_portal_first_item().is_visible():
            return True

class SelectSuggestionFloatingPortalFirstItem(SearchAtomicAction):
    async def perform_action(self):
        # print teh element
        if await self.search_result.suggestion_floating_portal_first_item().is_visible():
            await self.search_result.suggestion_floating_portal_first_item().click()
            await self.search_result.suggestion_floating_portal().wait_for(state="hidden")

    async def verify_action(self) -> bool:
        if await self.search_result.suggestion_floating_portal().is_hidden():
            return True
        return False