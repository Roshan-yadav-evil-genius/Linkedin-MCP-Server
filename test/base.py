"""Shared setup for manual Playwright test scripts under ``test/``."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent

CHROME_PROFILE = Path("./ChromeUserData")

DEFAULT_VIEWPORT: dict[str, int] = {"width": 1920, "height": 1080}

# Keys are Chromium CLI flags passed to launch; values are human-readable reasons (docs only).
CHROMIUM_LAUNCH_REASONS: dict[str, str] = {
    "--disable-blink-features=AutomationControlled": (
        "Disables the Blink 'AutomationControlled' feature, preventing Chromium from setting "
        "navigator.webdriver=true and exposing WebDriver-related automation markers in the JavaScript runtime."
    ),
    "--disable-background-timer-throttling": (
        "Prevents Chromium from throttling JavaScript timers (setTimeout, setInterval, "
        "requestAnimationFrame) in background tabs, allowing normal timer execution frequency."
    ),
    "--disable-backgrounding-occluded-windows": (
        "Stops Chromium from marking occluded or minimized windows as backgrounded, preventing "
        "reduced resource allocation due to window visibility state."
    ),
    "--disable-renderer-backgrounding": (
        "Prevents lowering of renderer process CPU scheduling priority when a tab is in the background, "
        "keeping it at normal foreground priority."
    ),
    "--disable-features=CalculateNativeWinOcclusion,IntensiveWakeUpThrottling,PageLifecycleFreeze": (
        "Disables native window occlusion, intensive wake-up throttling, and Page Lifecycle freeze so "
        "background/occluded tabs are not throttled or frozen."
    ),
}


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


def persistent_context_kwargs(
    *,
    user_data_dir: Path | None = None,
    headless: bool = False,
) -> dict[str, Any]:
    """Arguments for ``playwright.chromium.launch_persistent_context``."""
    return {
        "user_data_dir": user_data_dir or CHROME_PROFILE,
        "headless": headless,
        "args": list(CHROMIUM_LAUNCH_REASONS.keys()),
        "viewport": dict(DEFAULT_VIEWPORT),
    }
