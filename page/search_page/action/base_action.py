"""LinkedIn search-people page: mixin and base classes for atomic/molecular actions."""
import logging

from core.actions import AtomicAction, MolecularAction

from ..selectors.selector_resolver import LinkedInSearchPageSelectors
from playwright.async_api import Locator, Page


logger = logging.getLogger(__name__)


class LinkedInSearchPageMixin:
    def __init__(self, page: Page, **kwargs):
        super().__init__(page, **kwargs)
        self.search_result = LinkedInSearchPageSelectors(self.page)
    
    async def _wait_for_page_to_load(self):
        await self.search_result.all_filters_button().wait_for(state="visible", timeout=20000)
        logger.info("Search page loaded successfully")





class LinkedInBaseAtomicAction(LinkedInSearchPageMixin, AtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)


class LinkedInBaseMolecularAction(LinkedInSearchPageMixin, MolecularAction):
    def __init__(self, page: Page):
        super().__init__(page)
