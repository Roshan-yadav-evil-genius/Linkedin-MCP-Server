from enum import Enum
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field, model_validator

E = TypeVar("E", bound=Enum)


class SelectorEntry(BaseModel, Generic[E]):
    """
    One locator definition: key, optional parent for *local* selectors only, and two selector lists.

    ``local_selectors`` are chained with ``.or_()`` on ``get(parent)`` when ``parent`` is set,
    otherwise on the page. ``global_selectors`` are always chained on the page (parent ignored).
    """

    key: E = Field(..., description="Registry key for this entry (e.g. ProfilePageKey.CONNECT_BUTTON)")
    local_selectors: list[str] = Field(
        default_factory=list,
        description="XPath/CSS strings scoped under parent (or page if parent is None); fallbacks via .or_()",
    )
    global_selectors: list[str] = Field(
        default_factory=list,
        description="XPath/CSS strings always resolved from the page root; fallbacks via .or_()",
    )
    parent: Optional[E] = Field(
        default=None,
        description="Parent key for scoping local_selectors only; ignored for global_selectors",
    )

    model_config = {"frozen": True}

    @model_validator(mode="after")
    def _non_empty_selectors(self) -> "SelectorEntry[E]":
        if not self.local_selectors and not self.global_selectors:
            raise ValueError(f"SelectorEntry {self.key!r} must define at least one of local_selectors or global_selectors")
        return self


class SelectorRegistry(Generic[E]):
    """Registry of selector entries. Add entries via register(entry); duplicate key raises."""

    def __init__(self) -> None:
        self._entries: dict[E, SelectorEntry[E]] = {}

    def register(self, entry: SelectorEntry[E]) -> "SelectorRegistry[E]":
        """Add an entry. Key is taken from entry.key. Raises if key already registered."""
        if entry.key in self._entries:
            raise ValueError(f"Duplicate selector key: {entry.key}")
        if entry.parent is not None and entry.parent not in self._entries:
            raise ValueError(f"Parent key {entry.parent} must be registered before {entry.key}")
        self._entries[entry.key] = entry
        return self

    def get(self, key: E) -> Optional[SelectorEntry[E]]:
        """Return the entry for key, or None if not registered."""
        return self._entries.get(key)

    def __len__(self) -> int:
        return len(self._entries)
