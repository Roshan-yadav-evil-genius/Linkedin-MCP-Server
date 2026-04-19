"""Page-level orchestrator for LinkedIn messaging."""
import logging

from core.actions import BasePageAction

from .molecular_action import LoadChatAction, SendMessageAction
from .page_utility import PageUtility

logger = logging.getLogger(__name__)


class MessagingPage(PageUtility, BasePageAction):
    """Orchestrates messaging flows; delegates to molecular actions."""

    async def load_chat(self, user_name: str) -> bool:
        logger.info("Loading chat for recipient...")
        action = await LoadChatAction(self.page, user_name).accomplish()
        if not action.accomplished:
            logger.error("%s failed while loading chat", action.__class__.__name__)
        return action.accomplished

    async def send_message(self, message: str) -> bool:
        logger.info("Sending message...")
        action = await SendMessageAction(self.page, message).accomplish()
        if not action.accomplished:
            logger.error("%s failed while sending message", action.__class__.__name__)
        return action.accomplished
