import asyncio
import logging
from typing import Dict

from playwright.async_api import Page, async_playwright

from browser_profile_config import persistent_context_kwargs

logger = logging.getLogger(__name__)


class ChromeProfileManager:
    def __init__(self):
        self._playwright = None
        self.browser = None
        self.browser_context = None
        self._stopping = False
        self.page_instances: Dict[str, Page] = {}

        logger.debug(
            "ChromeProfileManager init"
        )
        self.persistent_context_kwargs = persistent_context_kwargs()

    async def start(self):
        logger.info(
            "Starting Playwright CDP session (headless=%s, user_data_dir=%s)",
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
        self.browser_context.on("close", lambda: asyncio.create_task(self.on_close()))
        logger.info("Playwright CDP session ready")

    async def on_close(self):
        if self._stopping:
            return
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

        def _cleanup_closed_page():
            cached = self.page_instances.get(session_id)
            if cached is page:
                self.page_instances.pop(session_id, None)
                logger.info("Removed closed page for session_id=%s", session_id)

        page.on("close", _cleanup_closed_page)
        self.page_instances[session_id] = page
        logger.info(
            "New page for session_id=%s (open sessions=%d)",
            session_id,
            len(self.page_instances),
        )
        return page

    async def get_page(self, session_id: str) -> Page:
        page = self.page_instances.get(session_id)
        if page and page.is_closed():
            logger.info("Cached page already closed for session_id=%s; recreating", session_id)
            self.page_instances.pop(session_id, None)
            page = None
        if not page:
            logger.debug("No page for session_id=%s; creating", session_id)
            return await self.new_page(session_id)
        logger.debug("Reusing page for session_id=%s", session_id)
        return page

    async def close_page(self, session_id: str) -> str:
        page = self.page_instances.pop(session_id, None)
        if not page:
            logger.info("No page found to close for session_id=%s", session_id)
            return "not_found"
        if page.is_closed():
            logger.info("Page already closed for session_id=%s", session_id)
            return "already_closed"
        try:
            await page.close()
            logger.info("Closed page for session_id=%s", session_id)
            return "closed"
        except Exception:
            logger.exception("Failed closing page for session_id=%s", session_id)
            return "error"

    async def stop(self):
        if self._stopping:
            return
        self._stopping = True
        n_pages = len(self.page_instances)
        if n_pages:
            logger.info("Stopping Playwright; closing %d managed session page(s)", n_pages)
            for session_id in list(self.page_instances.keys()):
                await self.close_page(session_id)
        try:
            if self.browser:
                await self.browser.close()
        except Exception:
            logger.exception("Failed to close CDP browser connection cleanly")
        finally:
            self.browser = None
            self.browser_context = None
        try:
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            logger.exception("Failed to stop Playwright cleanly")
        finally:
            self._playwright = None
            self._stopping = False

        logger.info("Playwright stopped")

    async def restart(self):
        logger.info("Restarting Playwright session")
        await self.stop()
        await self.start()