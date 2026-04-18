"""Selector registry for LinkedIn search-people page (schema mirrors profile page; replace placeholder selectors)."""

from core.models import SelectorEntry, SelectorRegistry

from .selector_keys import SearchPageKey

SEARCH_PAGE_SELECTORS: SelectorRegistry[SearchPageKey] = SelectorRegistry()

# Placeholder: use ``css=[data-automation-schema='search_page.<KEY>']`` until real LinkedIn search XPaths are added.

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.ALL_FILTERS_BUTTON,
        local_selectors=[],
        global_selectors=["//button[.//span[text()='All filters']]"],
        parent=None,
    )
)

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.FILTER_PANEL,
        local_selectors=[],
        global_selectors=["//aside"],
        parent=None,
    )
)

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.CONNECTIONS_OF_FILTER_BUTTON,
        local_selectors=[],
        global_selectors=["//button[.//span[text()='Add a connection']]"],
        parent=None,
    )
)

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.CONNECTIONS_OF_FILTER_INPUT,
        local_selectors=[],
        global_selectors=["//input[@placeholder='Add a connection']"],
        parent=None,
    )
)
SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.FOLLOWERS_OF_FILTER_BUTTON,
        local_selectors=[],
        global_selectors=["//button[.//span[text()='Add a creator']]"],
        parent=None,
    )
)

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.SUGGESTION_FLOATING_PORTAL,
        local_selectors=[],
        global_selectors=["//div[@data-floating-ui-portal]"],
        parent=None,
    )
)

SEARCH_PAGE_SELECTORS.register(
    SelectorEntry(
        key=SearchPageKey.SUGGESTION_FLOATING_PORTAL_ITEM,
        local_selectors=[],
        global_selectors=["(//div[@data-floating-ui-portal]//div[@role='option'])[1]"],
        parent=None,
    )
)