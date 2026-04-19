"""Headless smoke test for ChromeProfileManager lifecycle (optional CI / local check)."""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

_test_dir = Path(__file__).resolve().parent
_repo_root = _test_dir.parent
sys.path.insert(0, str(_repo_root))

from chrome_profile_manager import ChromeProfileManager, PageNotFoundError


async def main() -> None:
    tmp = Path(tempfile.mkdtemp())
    mgr = ChromeProfileManager(headless=True, user_data_dir=tmp)
    a = await mgr.open_page("about:blank")
    b = await mgr.open_page("about:blank")
    assert len(a) == 5 and a.isalnum()
    assert len(b) == 5 and b.isalnum()
    assert a != b
    mgr.get_page(a)
    mgr.get_page(b)
    await mgr.close_page(a)
    try:
        mgr.get_page(a)
    except PageNotFoundError:
        pass
    else:
        raise AssertionError("expected PageNotFoundError after close")
    await mgr.close_page(b)
    c = await mgr.open_page("about:blank")
    assert len(c) == 5
    await mgr.close_page(c)
    await mgr.shutdown()
    print("chrome_profile_manager_smoke: ok")


if __name__ == "__main__":
    asyncio.run(main())
