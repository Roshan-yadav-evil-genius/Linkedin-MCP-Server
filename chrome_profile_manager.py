"""Single-process Playwright persistent profile: one context, tabs keyed by short page_id."""
from __future__ import annotations

import asyncio
import logging
import secrets
import string
from pathlib import Path

from playwright.async_api import Page

from browser_profile_config import persistent_context_kwargs

logger = logging.getLogger(__name__)

PAGE_ID_LENGTH = 5
PAGE_ID_ALPHABET = string.ascii_letters + string.digits


class PageNotFoundError(KeyError):
    """Raised when ``page_id`` is not registered on the manager."""


class ChromeProfileManager:
    """Owns one Playwright driver and one persistent ``BrowserContext``; maps 5-char ids to tabs."""

    def __init__(self, *, headless: bool = False, user_data_dir: Path | None = None) -> None:
        self._headless = headless
        self._user_data_dir = user_data_dir
        self._lock = asyncio.Lock()
        self._playwright = None
        self._context = None
        self._pages: dict[str, Page] = {}
        self._interactive_profile_session_active = False

    def _allocate_page_id(self) -> str:
        assert self._lock.locked()
        while True:
            candidate = "".join(secrets.choice(PAGE_ID_ALPHABET) for _ in range(PAGE_ID_LENGTH))
            if candidate not in self._pages:
                return candidate

    async def _start_playwright_if_needed(self) -> None:
        assert self._lock.locked()
        if self._playwright is not None:
            return
        from playwright.async_api import async_playwright

        self._playwright = await async_playwright().start()
        logger.info("Playwright started")

    async def _launch_persistent_context_if_needed(self) -> None:
        assert self._lock.locked()
        if self._context is not None:
            return
        assert self._playwright is not None
        self._context = await self._playwright.chromium.launch_persistent_context(
            **persistent_context_kwargs(user_data_dir=self._user_data_dir, headless=self._headless)
        )
        for p in list(self._context.pages):
            await p.close()
        logger.info("Persistent Chromium context launched")

    async def ensure_ready(self) -> None:
        """Start Playwright and open the persistent context (no tracked tab yet)."""
        async with self._lock:
            if self._interactive_profile_session_active:
                raise RuntimeError(
                    "Interactive profile login is in progress; wait until the browser window is closed."
                )
            await self._start_playwright_if_needed()
            await self._launch_persistent_context_if_needed()

    async def run_interactive_profile_session(self, *, start_url: str = "about:blank") -> None:
        """
        Open a visible Chromium window (non-headless) on the persistent profile, then block until
        the user closes the browser. Use for manual sign-in to any site; cookies persist in
        ``user_data_dir``. Does not register a ``page_id`` (not compatible with ``open_page`` tabs:
        close all MCP-managed tabs first).
        """
        async with self._lock:
            if self._interactive_profile_session_active:
                raise RuntimeError("Interactive profile session is already running.")
            if self._pages:
                raise RuntimeError(
                    "Close all MCP-managed tabs with close_page before starting interactive login."
                )
            await self._start_playwright_if_needed()
            assert self._playwright is not None
            if self._context is not None:
                await self._context.close()
                self._context = None
            self._context = await self._playwright.chromium.launch_persistent_context(
                **persistent_context_kwargs(user_data_dir=self._user_data_dir, headless=False)
            )
            for p in list(self._context.pages):
                await p.close()
            page = await self._context.new_page()
            await page.goto(start_url, wait_until="domcontentloaded")
            self._interactive_profile_session_active = True
            context_ref = self._context
            logger.info("Interactive profile session started (headed); start_url=%s", start_url)

        try:
            await context_ref.wait_for_event("close", timeout=0)
        finally:
            async with self._lock:
                self._interactive_profile_session_active = False
                if self._context is context_ref:
                    self._context = None
                self._pages.clear()
            logger.info("Interactive profile session ended (browser closed)")

    async def open_page(self, url: str) -> str:
        async with self._lock:
            if self._interactive_profile_session_active:
                raise RuntimeError(
                    "Interactive profile login is in progress; wait until the browser window is closed."
                )
            await self._start_playwright_if_needed()
            await self._launch_persistent_context_if_needed()
            assert self._context is not None
            page = await self._context.new_page()
            page_id = self._allocate_page_id()
            self._pages[page_id] = page
            try:
                await page.goto(url, wait_until="load")
            except Exception:
                del self._pages[page_id]
                await page.close()
                logger.exception("open_page failed for url=%s", url)
                raise
            logger.info("open_page page_id=%s url=%s", page_id, url)
            return page_id

    async def close_page(self, page_id: str) -> str:
        async with self._lock:
            if self._interactive_profile_session_active:
                raise RuntimeError(
                    "Interactive profile login is in progress; wait until the browser window is closed."
                )
            page = self._pages.pop(page_id, None)
            if page is None:
                return f"No page registered for id {page_id!r}."
            try:
                await page.close()
            except Exception:
                logger.exception("close_page: error closing Playwright page for %s", page_id)
            logger.info("close_page page_id=%s", page_id)
            if not self._pages and self._context is not None:
                await self._context.close()
                self._context = None
                logger.info("Last tab closed; persistent context released")
            return f"Closed page {page_id!r}."

    def get_page(self, page_id: str) -> Page:
        if self._interactive_profile_session_active:
            raise RuntimeError(
                "Interactive profile login is in progress; wait until the browser window is closed."
            )
        page = self._pages.get(page_id)
        if page is None:
            raise PageNotFoundError(page_id)
        return page

    async def shutdown(self) -> None:
        async with self._lock:
            for page_id, page in list(self._pages.items()):
                try:
                    await page.close()
                except Exception:
                    logger.exception("shutdown: error closing page %s", page_id)
            self._pages.clear()
            if self._context is not None:
                await self._context.close()
                self._context = None
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None
            logger.info("ChromeProfileManager shutdown complete")


_chrome_profile_manager: ChromeProfileManager | None = None


def get_chrome_profile_manager() -> ChromeProfileManager:
    global _chrome_profile_manager
    if _chrome_profile_manager is None:
        _chrome_profile_manager = ChromeProfileManager()
    return _chrome_profile_manager
