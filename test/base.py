"""Shared setup for manual Playwright test scripts under ``test/``."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from browser_profile_config import (
    CHROME_PROFILE,
    CHROMIUM_LAUNCH_REASONS,
    DEFAULT_VIEWPORT,
    persistent_context_kwargs,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

__all__ = [
    "REPO_ROOT",
    "CHROME_PROFILE",
    "CHROMIUM_LAUNCH_REASONS",
    "DEFAULT_VIEWPORT",
    "configure_logging",
    "persistent_context_kwargs",
]


def configure_logging(level: int = logging.DEBUG) -> None:
    """Rich console logging; safe to call once per process (uses ``force`` on Python 3.8+)."""
    from rich.logging import RichHandler

    handler = RichHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    kwargs: dict[str, Any] = {"level": level, "handlers": [handler]}
    try:
        logging.basicConfig(**kwargs, force=True)
    except TypeError:
        logging.basicConfig(**kwargs)
