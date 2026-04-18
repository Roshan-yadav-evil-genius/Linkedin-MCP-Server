from .base_action import LinkedInBaseAtomicAction



class ClickOnAllFiltersButton(LinkedInBaseAtomicAction):

    async def perform_action(self):
        if await self.search_result.all_filters_button().is_visible():
            await self.search_result.all_filters_button().click()
            await self.search_result.filter_panel().wait_for(state="visible")
            

    async def verify_action(self) -> bool:
        if await self.search_result.filter_panel().is_visible():
            return True
        return False