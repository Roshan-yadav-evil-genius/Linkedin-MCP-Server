from core.models import SelectorEntry, SelectorRegistry

from .selector_keys import MessagingPageKey

MESSAGING_PAGE_SELECTORS: SelectorRegistry[MessagingPageKey] = SelectorRegistry()

MESSAGING_PAGE_SELECTORS.register(
    SelectorEntry(
        key=MessagingPageKey.SEARCH_PROFILE_INPUT,
        local_selectors=[],
        global_selectors=[
            'input[role="combobox"][placeholder*="name"]',
            'input[class*="msg-connections"]',
            'input[placeholder*="Type a name"]',
            'input[type="text"][aria-owns]',
        ],
        parent=None,
    )
)

MESSAGING_PAGE_SELECTORS.register(
    SelectorEntry(
        key=MessagingPageKey.SEARCH_RESULT_ROW,
        local_selectors=[],
        global_selectors=[
            '(//ul[@role="listbox"]//li[@role="option"])[1]'
        ],
        parent=None,
    )
)

MESSAGING_PAGE_SELECTORS.register(
    SelectorEntry(
        key=MessagingPageKey.MESSAGE_INPUT,
        local_selectors=[],
        global_selectors=[
            'div[role="textbox"][aria-label*="Write a message"]',
            'div[role="textbox"][aria-label*="message"i]',
            'div[class*="msg-form__contenteditable"]',
            'div[contenteditable="true"]',
        ],
        parent=None,
    )
)

MESSAGING_PAGE_SELECTORS.register(
    SelectorEntry(
        key=MessagingPageKey.SEND_BUTTON,
        local_selectors=[],
        global_selectors=[
            'button[type="submit"][class*="msg-form"]',
            'button[class*="send-btn"]',
            'button[class*="send-button"]',
            'form button[type="submit"]',
            'button[type="submit"]',
        ],
        parent=None,
    )
)
