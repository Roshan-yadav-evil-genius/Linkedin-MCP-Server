import asyncio
import logging
import sys
from pathlib import Path

_test_dir = Path(__file__).resolve().parent
_repo_root = _test_dir.parent
sys.path.insert(0, str(_repo_root))

from test.base import configure_logging, persistent_context_kwargs

configure_logging()
logger = logging.getLogger(__name__)

from playwright.async_api import async_playwright
from page.profile_page.actions import ProfilePage


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(**persistent_context_kwargs())

        page = await context.new_page()
        # profile_url = "https://www.linkedin.com/in/patricia-nittel-mha/"
        # profile_url = "https://www.linkedin.com/in/janet-higgins-165b6913/"
        # profile_url = "https://www.linkedin.com/in/harshit-goel-support/"
        profile_url = "https://www.linkedin.com/in/manish-kumar-prajapat-81a9893a5/"
        
        logger.info("Navigating to profile: %s", profile_url)
        await page.goto(profile_url, wait_until="load")
        page_action = ProfilePage(page)
        await page_action.wait_for_page_to_load()
        logger.info("Running follow_profile")
        await page_action.follow_profile()
        logger.info("Running unfollow_profile")
        await page_action.unfollow_profile()
        logger.info("Running send_connection_request")
        await page_action.send_connection_request()
        logger.info("Running withdraw_connection_request")
        await page_action.withdraw_connection_request()

        await context.wait_for_event("close", timeout=0)
        await context.close()


asyncio.run(main())
