"""LinkedIn messaging: shared utilities for selectors, URL validation, and load wait."""
import logging

from playwright.async_api import Page, expect

from ..selectors.selector_resolver import LinkedInMessagingPageSelectors

logger = logging.getLogger(__name__)


class PageUtility:
    """Wires messaging selectors, URL validation, and load wait."""

    def __init__(self, page: Page, **kwargs) -> None:
        super().__init__(page, **kwargs)
        self.messaging = LinkedInMessagingPageSelectors(self.page)
        self.page_url = page.url

    def is_valid_page(self) -> bool:
        return "/messaging/" in self.page_url

    async def wait_for_page_to_load(self) -> None:
        # New-thread UI shows both recipient combobox and compose box; OR-ing them
        # makes a single locator match two nodes and fails Playwright strict mode.
        await expect(self.messaging.search_profile_input()).to_be_visible(timeout=20_000)
        logger.info("Messaging page loaded successfully")
