from enum import Enum


class SearchPageKey(Enum):
    """Parallel keys to ``ProfilePageKey``; string values are search-page slugs (fill selectors in registry)."""

    ALL_FILTERS_BUTTON = "all_filters_button"
    FILTER_PANEL = "filter_panel"
    # Filter get Connections of
    CONNECTIONS_OF_FILTER_BUTTON = "connections_of_filter_button"
    CONNECTIONS_OF_FILTER_INPUT = "connections_of_filter_input"

    # Filter get Followers of
    FOLLOWERS_OF_FILTER_BUTTON = "followers_of_filter_button"
    FOLLOWERS_OF_FILTER_INPUT = "followers_of_filter_input"

    SUGGESTION_FLOATING_PORTAL = "suggestion_floating_portal"
    SUGGESTION_FLOATING_PORTAL_ITEM = "suggestion_floating_portal_item"