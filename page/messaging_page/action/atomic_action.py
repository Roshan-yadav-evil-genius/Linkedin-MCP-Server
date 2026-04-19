from playwright.async_api import Page
from core.actions import BaseAtomicAction
from .page_utility import PageUtility
from core.delays import DelayConfig
from core.human_behavior import human_typing
from playwright.async_api import expect


class FillSearchProfileInput(PageUtility, BaseAtomicAction):
    """
    Fill the search profile input with the given text.
    """

    def __init__(self, page: Page, user_name: str) -> None:
        super().__init__(page)
        self.user_name = user_name

    async def perform_action(self) -> None:
        await human_typing(
            self.messaging.search_profile_input(),
            self.user_name,
            config=DelayConfig(min_ms=50, max_ms=300),
        )

    async def verify_action(self) -> bool:
        value = await self.messaging.search_profile_input().input_value()
        if value == self.user_name:
            return True
        return False

class SelectSearchResultRow(PageUtility, BaseAtomicAction):

    async def perform_action(self) -> None:
        await self.messaging.search_result_row().wait_for(state="visible")
        await self.messaging.search_result_row().click()
        await self.messaging.search_result_row().wait_for(state="hidden")
    
    async def verify_action(self) -> bool:
        if not await self.messaging.search_result_row().is_visible():
            return True
        return False

class FillMessageInput(PageUtility, BaseAtomicAction):
    """
    Fill the message input with the given text.
    """

    def __init__(self, page: Page, message: str) -> None:
        super().__init__(page)
        self.message = message

    async def perform_action(self) -> None:
        await human_typing(
            self.messaging.message_input(),
            self.message,
            config=DelayConfig(min_ms=50, max_ms=300),
        )
    
    async def verify_action(self) -> bool:
        raw = await self.messaging.message_input().inner_text()
        return (raw or "").strip() == self.message.strip()

class ClickSendButton(PageUtility, BaseAtomicAction):
    """
    Click the send button.
    """

    async def perform_action(self) -> None:
        body = (await self.messaging.message_input().inner_text() or "").strip()
        if body:
            await self.messaging.send_button().click()
            await expect(self.messaging.send_button()).to_be_disabled()
        else:
            raise Exception("Message input is empty")

    async def verify_action(self) -> bool:
        body = (await self.messaging.message_input().inner_text() or "").strip()
        return body == ""