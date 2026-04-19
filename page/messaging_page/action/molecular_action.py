from playwright.async_api import Page
from core.actions import BaseMolecularAction
from .page_utility import PageUtility
from .atomic_action import FillSearchProfileInput,SelectSearchResultRow,FillMessageInput,ClickSendButton


class LoadChatAction(PageUtility, BaseMolecularAction):
    """
    Load the chat with the given user.
    """

    def __init__(self, page: Page, user_name: str) -> None:
        super().__init__(page)
        self.user_name = user_name
        self.chain_of_actions = [
            FillSearchProfileInput(page, user_name),
            SelectSearchResultRow(page)
        ]


class SendMessageAction(PageUtility, BaseMolecularAction):

    def __init__(self, page: Page, message: str) -> None:
        super().__init__(page)
        self.message = message
        self.chain_of_actions = [
            FillMessageInput(page, message),
            ClickSendButton(page)
        ]