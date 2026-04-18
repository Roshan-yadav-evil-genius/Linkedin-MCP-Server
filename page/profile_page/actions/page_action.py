"""Page-level orchestrator for LinkedIn profile page."""
import logging

from playwright.async_api import Page

from core.utils import extract_profile_user_id

from .molecular_action import (
    FollowProfile,
    SendConnectionRequest,
    UnfollowProfile,
    WithdrawConnectionRequest,
)
from .page_utility import ProfilePageAction

logger = logging.getLogger(__name__)


class ProfilePage(ProfilePageAction):
    """Orchestrates profile flows; delegates to molecular actions (SendConnectionRequest, WithdrawConnectionRequest, FollowProfile, UnfollowProfile)."""


    async def follow_profile(self):
        logger.info("Following profile...")
        action = await FollowProfile(self.page).accomplish()
        if not action.accomplished:
            logger.error("%s failed While Following Profile", action.__class__.__name__)
        return action.accomplished

    async def unfollow_profile(self):
        action = await UnfollowProfile(self.page).accomplish()
        if not action.accomplished:
            logger.error("%s failed While Unfollowing Profile", action.__class__.__name__)
        return action.accomplished

    async def send_connection_request(self, note: str = ""):
        logger.info("Sending connection request...")
        action = await SendConnectionRequest(self.page, note).accomplish()
        if not action.accomplished:
            logger.error("%s failed While Sending Connection Request", action.__class__.__name__)

        return action.accomplished

    async def withdraw_connection_request(self):
        logger.info("Withdrawing connection request...")
        action = await WithdrawConnectionRequest(self.page).accomplish()
        if not action.accomplished:
            logger.error("%s failed While Withdrawing Connection Request", action.__class__.__name__)
        return action.accomplished
