from playwright.async_api import Locator, Page

from core.selector_resolver import SelectorResolver


from .selector_keys import MessagingPageKey
from .selector_registry import MESSAGING_PAGE_SELECTORS


class LinkedInMessagingPageSelectors(SelectorResolver):
    """
    Selector resolver for LinkedIn messaging page.
    """

    def __init__(self, page: Page) -> None:
        super().__init__(page, MESSAGING_PAGE_SELECTORS)
    
    def search_profile_input(self) -> Locator:
        return self.get(MessagingPageKey.SEARCH_PROFILE_INPUT)
    
    def search_result_row(self) -> Locator:
        return self.get(MessagingPageKey.SEARCH_RESULT_ROW)
    
    def message_input(self) -> Locator:
        return self.get(MessagingPageKey.MESSAGE_INPUT)
    
    def send_button(self) -> Locator:
        return self.get(MessagingPageKey.SEND_BUTTON)