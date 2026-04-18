"""Profile page: shared utilities for selectors, validation, waits, and step bases."""
import logging

from core.actions import BaseAtomicAction, BaseMolecularAction, BasePageAction
from core.utils import is_valid_linkedin_profile_url
from playwright.async_api import Locator, Page

from ..selectors.selector_resolver import LinkedInProfilePageSelectors

from .profile_state import ConnectionStatus, FollowingStatus

logger = logging.getLogger(__name__)


class PageUtility:
    """Wires profile selectors, URL validation, and load wait for orchestrators and steps."""

    def __init__(self, page: Page, **kwargs) -> None:
        super().__init__(page, **kwargs)
        self.profile = LinkedInProfilePageSelectors(self.page)
        self.profile_url = page.url

    def is_valid_page(self) -> bool:
        return is_valid_linkedin_profile_url(self.profile_url)

    async def wait_for_page_to_load(self) -> None:
        await self.profile.activity_section_text().wait_for(state="visible", timeout=20000)

    async def _get_connection_status(self) -> ConnectionStatus:
        if await self.profile.connect_button().is_visible():
            return ConnectionStatus.NOT_CONNECTED
        if await self.profile.pending_button().is_visible():
            return ConnectionStatus.PENDING
        return ConnectionStatus.CONNECTED

    async def _get_following_status(self) -> FollowingStatus:
        if await self.profile.follow_button().count():
            return FollowingStatus.NOT_FOLLOWING
        return FollowingStatus.FOLLOWING

    async def _wait_for_dialog(self, context: str = "action") -> Locator | None:
        logger.debug("Waiting for dialog after %s", context)
        dialog = self.profile.dialog()
        try:
            await dialog.wait_for(state="visible", timeout=5000)
            logger.debug("Dialog appeared successfully")
            return dialog
        except Exception as e:
            logger.warning("Dialog did not appear after %s: %s", context, e)
            return None


class ProfilePageAction(PageUtility, BasePageAction):
    """Combines PageUtility with BasePageAction; subclass as ProfilePage for orchestration APIs."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)


class ProfileAtomicAction(PageUtility, BaseAtomicAction):
    def __init__(self, page: Page) -> None:
        super().__init__(page)


class ProfileMolecularAction(PageUtility, BaseMolecularAction):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
