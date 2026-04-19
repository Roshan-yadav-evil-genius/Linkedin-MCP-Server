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
from page.messaging_page.action.page_action import MessagingPage


async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(**persistent_context_kwargs())

        page = await context.new_page()
        profile_url = "https://www.linkedin.com/messaging/thread/new/"
        
        logger.info("Navigating to profile: %s", profile_url)
        await page.goto(profile_url, wait_until="load")
        
        messaging_page = MessagingPage(page)
        await messaging_page.load_chat("Roshan")
        await messaging_page.send_message("Hello, how are you?")

        await context.wait_for_event("close", timeout=0)
        await context.close()


asyncio.run(main())
