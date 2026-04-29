import asyncio
from playwright.async_api import async_playwright
from typing import Dict
from playwright.async_api import Page

import logging

logger = logging.getLogger(__name__)

class ChromeProfileManager:
    def __init__(self, **kwargs):

        # ================================================
        self.user_data_dir = kwargs.get("user_data_dir")
        self.headless = kwargs.get("headless", False)
        self.args = kwargs.get("args", ["--start-maximized"])
        self.viewport = kwargs.get("viewport", {"width": 1920, "height": 800})

        # ================================================
        self._playwright = None
        self.browser_context = None
        self.page_instances:Dict[str, Page] = {}

    async def start(self):
        self._playwright = await async_playwright().start()
        self.browser_context = await self._playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=self.headless,
            args=self.args
        )
        self.browser_context.on("close", self.on_close)
    

    async def on_close(self):
        await self.stop()

    async def new_page(self, session_id: str):
        
        if not self.browser_context or not self._playwright:
            await self.restart()
        
        page = await self.browser_context.new_page()
        self.page_instances[session_id] = page
        return page

    async def get_page(self, session_id: str) -> Page:
        if session_id not in self.page_instances:
            return await self.new_page(session_id)
        return self.page_instances.get(session_id)

    async def close_page(self, session_id: str):
        page = self.page_instances.get(session_id)
        if page:
            await page.close()
            del self.page_instances[session_id]

    async def stop(self):
        if self.browser_context:
            await self.browser_context.close()
            self.browser_context = None

        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    async def restart(self):
        await self.stop()
        await self.start()