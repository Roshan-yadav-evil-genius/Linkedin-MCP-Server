from playwright.async_api import async_playwright
from playwright.async_api import Page
from typing import Dict

import logging

from browser_profile_config import persistent_context_kwargs

logger = logging.getLogger(__name__)


class ChromeProfileManager:
    def __init__(self):
        # ================================================
        self._playwright = None
        self.browser_context = None
        self.page_instances: Dict[str, Page] = {}

        logger.debug(
            "ChromeProfileManager init"
        )
        self.persistent_context_kwargs = persistent_context_kwargs()

    async def start(self):
        logger.info(
            "Starting Playwright persistent context (headless=%s, user_data_dir=%s)",
            self.persistent_context_kwargs["headless"],
            self.persistent_context_kwargs["user_data_dir"],
        )
        try:
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.connect_over_cdp("http://localhost:9222")
            self.browser_context = self.browser.contexts[0]
        except Exception as e:
            await self.stop()
            raise e
        self.browser_context.on("close", self.on_close)
        logger.info("Playwright persistent context ready")

    async def on_close(self):
        logger.warning(
            "Browser context closed (external or crash); stopping Playwright session"
        )
        await self.stop()

    async def new_page(self, session_id: str):
        if not self.browser_context or not self._playwright:
            logger.info(
                "No active browser context; restarting before new_page session_id=%s",
                session_id,
            )
            await self.restart()

        page = await self.browser_context.new_page()
        self.page_instances[session_id] = page
        logger.info(
            "New page for session_id=%s (open sessions=%d)",
            session_id,
            len(self.page_instances),
        )
        return page

    async def get_page(self, session_id: str) -> Page:
        if session_id not in self.page_instances:
            logger.debug("No page for session_id=%s; creating", session_id)
            return await self.new_page(session_id)
        logger.debug("Reusing page for session_id=%s", session_id)
        return self.page_instances.get(session_id)

    async def stop(self):
        n_pages = len(self.page_instances)
        if n_pages:
            logger.info(
                "Stopping Playwright; dropping %d session page(s) without explicit close",
                n_pages,
            )
            self.page_instances.clear()
        try:
            if self.browser_context:
                await self.browser_context.close()
        except Exception as e:
            self.browser_context = None
        try:    
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
        except Exception as e:
            self._playwright = None

        logger.info("Playwright stopped")

    async def restart(self):
        logger.info("Restarting Playwright session")
        await self.stop()
        await self.start()