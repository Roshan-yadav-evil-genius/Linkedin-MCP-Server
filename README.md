# LinkedIn MCP

**LinkedIn MCP** is a [Model Context Protocol](https://modelcontextprotocol.io/) server that connects an AI assistant to LinkedIn through a real browser session. The assistant can open pages, read what is on screen in plain text, run LinkedIn-focused actions (such as search, connection requests, and messaging), and fall back to custom in-page actions when needed. Your sign-in state can be kept between sessions so repeat tasks do not always require logging in again.

## Who it is for

This project suits individuals or teams who want an AI agent to help with LinkedIn workflows—for example finding people, narrowing lists with filters, reading result pages, taking simple actions on a member’s profile, or sending a message—while a human handles sign-in when LinkedIn asks for it (password, second factor, or other checks).

## How the agent typically works

1. **Sign in when needed** — Call ``linkedin_login`` to open the LinkedIn login page; the user completes authentication in the browser.
2. **Work on the session page** — One browser tab per MCP session. Tools navigate or act on that tab. Most LinkedIn actions expect the correct kind of page (profile URL, people search, messaging).
3. **Act or read** — Use the ``linkedin_*`` tools below. To see names and lists as text, call ``linkedin_get_page_content``. For behavior no named tool covers, use ``linkedin_run_javascript`` sparingly.
4. **Close when finished** — ``linkedin_close_page`` closes the tab for this session when you want a clean slate.

## Capabilities (tool names)

All exported MCP tools use the ``linkedin_`` prefix so they are easy to tell apart from generic browser MCPs.

### Session and browsing

- ``linkedin_login`` — Open LinkedIn login for manual sign-in.
- ``linkedin_open_page`` — Navigate to a LinkedIn URL only (``https://…linkedin.com/…``).
- ``linkedin_close_page`` — Close the session tab.
- ``linkedin_get_page_content`` — Read the current page as Markdown-style text.
- ``linkedin_run_javascript`` — Run JS in the page and return the result (escape hatch).

### Member profile

Provide ``profile_url`` for each action.

- ``linkedin_send_connection_request`` — Send an invite (optional `note`); pass ``withdraw=True`` to cancel a pending invite.
- ``linkedin_follow_profile`` — Follow someone’s public updates; pass ``unfollow=True`` to stop following.

### People search

- ``linkedin_search_people`` — Search by keywords; set ``in_my_connections=True`` to limit to your 1st-degree network.
- ``linkedin_apply_search_filters`` — Narrow people results using the filter schema.
- ``linkedin_search_next_page`` / ``linkedin_search_previous_page`` — Paginate people search results.

After search or filters change the screen, use ``linkedin_get_page_content`` to read the list.

### Messaging

- ``linkedin_open_chat_with`` — Open a chat with someone by display name (no message sent).
- ``linkedin_send_message_to`` — Send a DM (recipient name + message body).

## What changes the site vs what only reads

| Changes LinkedIn | Reads only |
|------------------|------------|
| Connection invite / withdraw; follow / unfollow; messaging tools | ``linkedin_get_page_content`` |
| Open search or navigate | Same read step after load |
| Apply filters; next/previous search page | |
| ``linkedin_run_javascript`` when it clicks/types | ``linkedin_run_javascript`` used only to read |

## Example flows

1. **Discover candidates** — ``linkedin_search_people``, optionally ``linkedin_apply_search_filters`` and pagination tools, then ``linkedin_get_page_content`` to summarize.
2. **Connect** — ``linkedin_send_connection_request`` with the profile URL and optional note. To withdraw a pending invite, same tool with ``withdraw=True``.
3. **Message** — ``linkedin_send_message_to`` with recipient name and text (or ``linkedin_open_chat_with`` first if you want to verify the thread opens).

## Expectations and limits

LinkedIn’s interface and rules change over time. Accounts can hit limits or see controls disabled. Use automation responsibly and comply with LinkedIn’s terms and applicable laws.

## For contributors

Implementation and selector architecture are described in [CoreArchitecture.md](CoreArchitecture.md).
