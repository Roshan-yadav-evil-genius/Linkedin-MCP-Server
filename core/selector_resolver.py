import logging
from enum import Enum
from typing import TypeVar

from playwright.async_api import Locator, Page

from .models import SelectorEntry, SelectorRegistry

logger = logging.getLogger(__name__)

E = TypeVar("E", bound=Enum)


def _chain_locators(base: Page | Locator, strings: list[str]) -> Locator:
    """Chain ``strings`` on ``base`` with ``.or_()`` (first is primary). ``strings`` must be non-empty."""
    locator = base.locator(strings[0])
    for selector in strings[1:]:
        locator = locator.or_(base.locator(selector))
    return locator


class SelectorResolver:
    """Resolves selector keys to Playwright locators using a registry. Reusable by any site (LinkedIn, etc.)."""

    def __init__(self, page: Page, registry: SelectorRegistry[E]) -> None:
        self.page = page
        self.registry = registry
        self._locator_cache: dict = {}
        if len(registry) == 0:
            logger.warning("SelectorResolver initialized with empty registry")

    def get(self, key: E) -> Locator:
        """
        Resolve a key to a locator.

        Builds a **local** branch from ``local_selectors`` scoped under ``get(parent)``
        when ``parent`` is set, else under ``page``. Builds a **global** branch from
        ``global_selectors`` on ``page`` only. When both exist, combines as
        ``local.or_(global)`` (locals preferred first).
        """
        if key in self._locator_cache:
            return self._locator_cache[key]

        entry = self.registry.get(key)
        if not entry:
            logger.error("No selector found in registry for key: %s", key)
            raise ValueError(f"No selector found in registry for key: {key}")

        local_sel = entry.local_selectors
        global_sel = entry.global_selectors
        parent_key = entry.parent

        if not local_sel and not global_sel:
            logger.error("No selectors defined for key: %s", key)
            raise ValueError(f"No selectors defined for key: {key}")

        branches: list[Locator] = []

        if local_sel:
            if parent_key is not None:
                base: Page | Locator = self.get(parent_key)
            else:
                base = self.page
            branches.append(_chain_locators(base, local_sel))

        if global_sel:
            branches.append(_chain_locators(self.page, global_sel))

        if len(branches) == 1:
            locator = branches[0]
        else:
            locator = branches[0].or_(branches[1])

        self._locator_cache[key] = locator
        return locator

    def clear_cache(self) -> None:
        """Clear the locator cache. Call after navigation if needed."""
        logger.debug("Locator cache cleared (%d entries)", len(self._locator_cache))
        self._locator_cache.clear()
