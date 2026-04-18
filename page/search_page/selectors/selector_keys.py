from enum import Enum


class SearchPageKey(Enum):
    """Parallel keys to ``ProfilePageKey``; string values are search-page slugs (fill selectors in registry)."""

    ALL_FILTERS_BUTTON = "all_filters_button"
    FILTER_PANEL = "filter_panel"
