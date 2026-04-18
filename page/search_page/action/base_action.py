"""LinkedIn search-people page: mixin and base classes for atomic/molecular actions."""
import logging

from core.actions import AtomicAction, CooperativePageStepInit, MolecularAction

from ..selectors.selector_resolver import LinkedInSearchPageSelectors
from playwright.async_api import Page


logger = logging.getLogger(__name__)


class LinkedInSearchPageMixin:
    def __init__(self, page: Page, **kwargs):
        super().__init__(page, **kwargs)
        self.search_result = LinkedInSearchPageSelectors(self.page)
        

class LinkedInBaseAtomicAction(CooperativePageStepInit, LinkedInSearchPageMixin, AtomicAction):
    pass


class LinkedInBaseMolecularAction(CooperativePageStepInit, LinkedInSearchPageMixin, MolecularAction):
    pass
