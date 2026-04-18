"""Selector registry for LinkedIn profile page."""

from core.models import SelectorEntry, SelectorRegistry

from .selector_keys import ProfilePageKey

PROFILE_PAGE_SELECTORS: SelectorRegistry[ProfilePageKey] = SelectorRegistry()

# Main Profile Action Bar (Root element - no parent)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.PROFILE_CARD,
        local_selectors=[],
        global_selectors=[
            "(//section[contains(@class,'artdeco-card')])[1]//ul[.//li[contains(normalize-space(.),'connections')]]/following-sibling::*[1]",
            "//section[contains(@componentkey, 'profile.card') and contains(@componentkey, 'Topcard')]",
        ],
        parent=None,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.ACTIVITY_SECTION_TEXT,
        local_selectors=[],
        global_selectors=[
            "//section[contains(@class,'artdeco-card')]//span[normalize-space()='Activity' and not(contains(@class,'visually-hidden'))]",
            "//div[contains(@componentkey, 'profile.card') and contains(@componentkey, 'Activity')]//*[normalize-space()='Activity' and not(contains(@class,'visually-hidden'))]",
        ],
        parent=None,
    )
)
# Buttons scoped to PROFILE_CARD
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.CONNECT_BUTTON,
        local_selectors=[
            # "//button[.//span[text()='Connect']]",
            "//div[@role='button'][.//span[text()='Connect']]",
        ],
        global_selectors=[
            "(//section[contains(@componentkey, 'profile.card') and contains(@componentkey, 'Topcard')]//*[self::a or self::button][.//span[text()='Connect']])[1]"
        ],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.PENDING_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Pending']]",
            "//div[@role='button'][.//span[text()='Pending']]",
        ],
        global_selectors=[
            "(//section[contains(@componentkey, 'profile.card') and contains(@componentkey, 'Topcard')]//*[self::a or self::button][.//span[text()='Pending']])[1]"

        ],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.MESSAGE_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Message']]",
            "//div[@role='button'][.//span[text()='Message']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.MORE_MENU_BUTTON,
        local_selectors=[
            "//button[.//span[text()='More']]",
            "//button[@aria-label='More actions']",
        ],
        global_selectors=[],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.MORE_MENU_DIALOG,
        local_selectors=[],
        global_selectors=[
            "//div[@role='menu']"
        ],
        parent=None
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.FOLLOW_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Follow']]",
            "//div[@role='button'][.//span[text()='Follow']]",
        ],
        global_selectors=["//div[@role='menuitem'][.//*[text()='Follow']]"],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.UNFOLLOW_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Unfollow']]",
            "//div[@role='button'][.//span[text()='Unfollow']]",
        ],
        global_selectors=["//div[@role='menuitem'][.//*[text()='Following']]"],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.REMOVE_CONNECTION_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Remove connection']]",
            "//div[@role='button'][.//span[text()='Remove connection']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.PROFILE_CARD,
    )
)
# Dialogs (global)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.DIALOG,
        local_selectors=[],
        global_selectors=[
            "//div[@role='dialog']",
            "//div[@role='alertdialog']",
            "//dialog[@open]",
            "div[role='dialog']"
            
        ],
        parent=None,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.WITHDRAW_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Withdraw']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.DIALOG_UNFOLLOW_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Unfollow']]",
            "//div[@role='button'][.//span[text()='Unfollow']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
# Dialog Actions (scoped to DIALOG)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.ADD_NOTE_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Add a note']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.SEND_WITHOUT_NOTE_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Send without a note']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.SEND_BUTTON,
        local_selectors=[
            "//button[.//span[text()='Send']]",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
PROFILE_PAGE_SELECTORS.register(
    SelectorEntry(
        key=ProfilePageKey.ADD_NOTE_INPUT,
        local_selectors=[
            "//textarea[@name='message']",
        ],
        global_selectors=[],
        parent=ProfilePageKey.DIALOG,
    )
)
