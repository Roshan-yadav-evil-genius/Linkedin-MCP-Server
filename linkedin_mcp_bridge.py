"""Resolve MCP ``page_id`` handles to Playwright pages and page orchestrators (SRP: server stays thin)."""
from __future__ import annotations

import logging
from typing import Tuple

from playwright.async_api import Page

from chrome_profile_manager import PageNotFoundError, get_chrome_profile_manager
from page.profile_page.actions.page_action import ProfilePage
from page.search_page.action.page_action import SearchPage

logger = logging.getLogger(__name__)


def resolve_tracked_page(page_id: str) -> Page | str:
    """Return a live ``Page`` for ``page_id``, or a human-readable error string."""
    try:
        return get_chrome_profile_manager().get_page(page_id)
    except PageNotFoundError:
        return f"Unknown or closed page_id: {page_id!r}."
    except RuntimeError as e:
        return str(e)


async def run_profile_page(page_id: str) -> Tuple[ProfilePage | None, str | None]:
    """
    Return ``(ProfilePage, None)`` after load wait, or ``(None, error)`` if resolve/URL/load fails.
    """
    resolved = resolve_tracked_page(page_id)
    if isinstance(resolved, str):
        return None, resolved
    profile = ProfilePage(resolved)
    if not profile.is_valid_page():
        return None, "This tab is not a LinkedIn profile URL. Use open_page with a member profile URL first."
    try:
        await profile.wait_for_page_to_load()
    except Exception as e:
        logger.exception("Profile wait_for_page_to_load failed page_id=%s", page_id)
        return None, f"Profile page did not become ready in time: {e}"
    return profile, None


async def run_search_page(page_id: str) -> Tuple[SearchPage | None, str | None]:
    """
    Return ``(SearchPage, None)`` after load wait, or ``(None, error)`` if resolve/URL/load fails.
    """
    resolved = resolve_tracked_page(page_id)
    if isinstance(resolved, str):
        return None, resolved
    search = SearchPage(resolved)
    if not search.is_valid_page():
        return None, (
            "This tab is not LinkedIn people search (/search/results/people/). "
            "Use search_people, open_page with a people search URL, or navigate first."
        )
    try:
        await search.wait_for_page_to_load()
    except Exception as e:
        logger.exception("Search wait_for_page_to_load failed page_id=%s", page_id)
        return None, f"Search page did not become ready in time: {e}"
    return search, None
