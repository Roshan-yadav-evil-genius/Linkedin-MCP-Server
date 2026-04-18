"""Atomic actions for LinkedIn profile page."""
import logging

from .page_utility import ProfileAtomicAction
from core.delays import DelayConfig
from core.human_behavior import human_typing
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class ClickOnMoreButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        if not await self.profile.more_menu_dialog().is_visible():
            logger.info("Clicking on more menu button")
            await self.profile.more_menu_button().click()
            logger.info("Waiting for more menu dialog to appear")
            await self.profile.more_menu_dialog().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.profile.more_menu_dialog().is_visible():
            return True
        return False


class ClickOnConnectButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        if await self.profile.connect_button().is_visible():
            await self.profile.connect_button().click()
            await self._wait_for_dialog("clicking Connect")

    async def verify_action(self) -> bool:
        if await self.profile.dialog().is_visible():
            return True
        return False


class ClickOnAddNoteButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        if await self.profile.dialog().is_visible():
            await self.profile.add_note_button().click()
            await self.profile.add_note_input().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.profile.add_note_input().is_visible():
            return True
        return False


class ClickOnSendWithoutNoteButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.send_without_note_button().click(timeout=10000)
        await self.profile.pending_button().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.profile.pending_button().is_visible():
            return True
        return False


class FillAddNoteInput(ProfileAtomicAction):
    def __init__(self, page: Page, invitation_note: str):
        super().__init__(page)
        self.invitation_note = invitation_note

    async def perform_action(self):
        await human_typing(
            self.profile.add_note_input(),
            self.invitation_note,
            config=DelayConfig(min_ms=50, max_ms=300),
        )

    async def verify_action(self) -> bool:
        if await self.profile.add_note_input().input_value() == self.invitation_note:
            return True
        return False


class SubmitInvitationNote(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.send_button().click()
        await self.page.wait_for_timeout(500)

    async def verify_action(self) -> bool:
        if not await self.profile.send_button().is_visible():
            return True
        return False


class ClickOnPendingButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.pending_button().click()
        await self.profile.withdraw_button().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.profile.withdraw_button().is_visible():
            return True
        return False


class ClickOnWithdrawButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.withdraw_button().click()
        await self.profile.withdraw_button().wait_for(state="hidden")

    async def verify_action(self) -> bool:
        if not await self.profile.withdraw_button().is_visible():
            return True
        return False


class ClickOnUnfollowButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.unfollow_button().click()
        await self.profile.dialog_unfollow_button().wait_for(state="visible")

    async def verify_action(self) -> bool:
        if await self.profile.dialog_unfollow_button().is_visible():
            return True
        return False


class ClickOnDialogUnfollowButton(ProfileAtomicAction):
    def __init__(self, page: Page):
        super().__init__(page)

    async def perform_action(self):
        await self.profile.dialog_unfollow_button().click()
        await self.profile.dialog_unfollow_button().wait_for(state="hidden")

    async def verify_action(self) -> bool:
        if not await self.profile.dialog_unfollow_button().is_visible():
            return True
        return False
