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
            await self.search_result.connections_of_filter_input().wait_for(
                state="visible"
            )

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

    async def verify_action(self) -> bool:
        value = await self.search_result.connections_of_filter_input().input_value()
        if value == self.connection_name:
            return True
        return False


class SelectSuggestionFloatingPortalFirstItem(SearchAtomicAction):
    async def perform_action(self):
        # Locator is returned synchronously; await only the async checks/actions on it.
        first_item = self.search_result.suggestion_floating_portal_first_item()

        if await first_item.is_visible():
            await first_item.click()
            await self.search_result.selected_suggestion_floating_portal_item().wait_for(state="visible")
        else:
            raise Exception("Not Valid Person is available with specified Name")

    async def verify_action(self) -> bool:
        if await self.search_result.selected_suggestion_floating_portal_item().is_visible():
            return True
        return False


class ClickOnFollowersOfFilterButton(SearchAtomicAction):
    async def perform_action(self):
        if await self.search_result.followers_of_filter_button().is_visible():
            await self.search_result.followers_of_filter_button().click()
            await self.search_result.followers_of_filter_input().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.search_result.followers_of_filter_input().is_visible():
            return True
        return False

class FillFollowersOfFilterInput(SearchAtomicAction):
    def __init__(self, page: Page, follower_name: str):
        super().__init__(page)
        self.follower_name = follower_name

    async def perform_action(self):
        if await self.search_result.followers_of_filter_input().is_visible():
            await human_typing(
                self.search_result.followers_of_filter_input(),
                self.follower_name,
                config=DelayConfig(min_ms=50, max_ms=300),
            )

    async def verify_action(self) -> bool:
        value = await self.search_result.followers_of_filter_input().input_value()
        if value == self.follower_name:
            return True
        return False

class ClickOnApplyFiltersButton(SearchAtomicAction):
    async def perform_action(self):
        if await self.search_result.apply_filters_button().is_visible():
            await self.search_result.apply_filters_button().click()
            await self.search_result.all_filters_button().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.search_result.all_filters_button().is_visible():
            return True
        return False


class ClickOnPaginationNextButton(SearchAtomicAction):
    async def perform_action(self):
        if await self.search_result.pagination_next_button().is_visible():
            self.current_page = await self.search_result.pagination_current_page().text_content()
            self.current_page = int(self.current_page)
            await self.search_result.pagination_next_button().click()
            await self.search_result.pagination_current_page().wait_for(state="visible")


    async def verify_action(self) -> bool:
        new_page = await self.search_result.pagination_current_page().text_content()
        new_page = int(new_page)
        if new_page == self.current_page + 1:
            return True
        return False

class ClickOnPaginationPreviousButton(SearchAtomicAction):
    async def perform_action(self):
        if await self.search_result.pagination_previous_button().is_visible():
            self.current_page = await self.search_result.pagination_current_page().text_content()
            self.current_page = int(self.current_page)
            await self.search_result.pagination_previous_button().click()
            await self.search_result.pagination_current_page().wait_for(state="visible")

    async def verify_action(self) -> bool:
        new_page = await self.search_result.pagination_current_page().text_content()
        new_page = int(new_page)
        if new_page == self.current_page - 1:
            return True
        return False