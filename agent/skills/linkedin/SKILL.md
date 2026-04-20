---
name: linkedin
description: Run LinkedIn prospecting, connection, follow/unfollow, and messaging workflows with deterministic tool sequences. Use when the user asks to search LinkedIn people, filter results, paginate, connect with someone, follow profiles, withdraw invites, or send LinkedIn messages.
---

# LinkedIn

## Overview

Use this skill for LinkedIn-specific workflows using tools exposed by `server.py`. Keep actions evidence-driven: read state, act once, then verify with tool output or fresh page content.

## Instructions

### Step 1: Route to the right objective
Pick one objective first: prospect, find existing connections, take profile action, or message.  
Then choose the workflow:

- **Prospecting:** `search_people(query)` -> `get_page_content(page_id)` -> optional `apply_filters(page_id, filter)` -> `get_page_content(page_id)`.
- **Existing connections:** `search_person_in_my_connections(query)` -> `get_page_content(page_id)`.
- **Pagination:** `click_on_pagination_next_button(page_id)` or `click_on_pagination_previous_button(page_id)` -> always `get_page_content(page_id)`.
- **Profile actions:** open profile tab if needed (`open_page(profile_url)`) -> verify profile with `get_page_content` -> run one action (`send_connection_request`, `withdraw_connection_request`, `follow_profile`, `unfollow_profile`).
- **Messaging:** `open_chat_window_of(user_name)` once -> reuse returned `page_id` for all `send_messaging_message(page_id, message)` calls.

### Step 2: Verify every state-changing action
After filters, pagination, navigation, or JavaScript interaction, re-read with `get_page_content`.  
Do not report success unless the tool explicitly returned success or the page evidence confirms it.

### Step 3: Handle failures with minimal recovery
- **Search/filter fails:** confirm tab context, re-apply valid filter payload, re-read content.
- **Profile action fails:** re-check profile context and current relationship state, then report exact tool failure text.
- **Messaging gate fails:** run `open_chat_window_of(user_name)` again, use new `page_id`, retry `send_messaging_message`.
- **Session/auth issue:** run `login`, then restart from the smallest necessary step.

## Best Practices

- Keep `page_id` ownership clear per workflow and reuse chat `page_id` for follow-ups.
- Personalize outreach only with observed profile evidence; mark unknowns explicitly.
- Use one clear CTA in outreach messages and avoid fabricated claims.
- Prefer dedicated LinkedIn tools over generic `run_javascript` when available.
- Return objective, tool sequence, `page_id` values, evidence, outcomes, unknowns, and next step.

## Examples

### Example 1: Prospect, filter, then connect

**User Request:** "Find SaaS founders in India and send one connection request."

**Approach:**
1. Run `search_people("founder saas india")` and capture `page_id`.
2. Run `get_page_content(page_id)` to list visible candidates.
3. Run `apply_filters(page_id, filter)` and re-read with `get_page_content(page_id)`.
4. Open selected profile with `open_page(profile_url)` and verify with `get_page_content`.
5. Send invite using `send_connection_request(profile_page_id, note)` and report exact outcome.

### Example 2: Message an existing connection

**User Request:** "Message Jane Doe, who is already in my connections."

**Approach:**
1. Run `search_person_in_my_connections("Jane Doe")` and review results via `get_page_content`.
2. Open chat once using `open_chat_window_of("Jane Doe")`.
3. Send initial note with `send_messaging_message(chat_page_id, message)`.
4. Send follow-up with the same `chat_page_id` and confirm tool success responses.
---
name: linkedin
description: Run LinkedIn prospecting, connection, follow/unfollow, and messaging workflows with deterministic tool sequences. Use when the user asks to search LinkedIn people, filter results, paginate, connect with someone, follow profiles, withdraw invites, or send LinkedIn messages.
---

# LinkedIn

## Overview

Use this skill for LinkedIn-specific workflows using tools exposed by `server.py`. Keep actions evidence-driven: read state, act once, then verify with tool output or fresh page content.

## Instructions

### Step 1: Route to the right objective
Pick one objective first: prospect, find existing connections, take profile action, or message.  
Then choose the workflow:

- **Prospecting:** `search_people(query)` -> `get_page_content(page_id)` -> optional `apply_filters(page_id, filter)` -> `get_page_content(page_id)`.
- **Existing connections:** `search_person_in_my_connections(query)` -> `get_page_content(page_id)`.
- **Pagination:** `click_on_pagination_next_button(page_id)` or `click_on_pagination_previous_button(page_id)` -> always `get_page_content(page_id)`.
- **Profile actions:** open profile tab if needed (`open_page(profile_url)`) -> verify profile with `get_page_content` -> run one action (`send_connection_request`, `withdraw_connection_request`, `follow_profile`, `unfollow_profile`).
- **Messaging:** `open_chat_window_of(user_name)` once -> reuse returned `page_id` for all `send_messaging_message(page_id, message)` calls.

### Step 2: Verify every state-changing action
After filters, pagination, navigation, or JavaScript interaction, re-read with `get_page_content`.  
Do not report success unless the tool explicitly returned success or the page evidence confirms it.

### Step 3: Handle failures with minimal recovery
- **Search/filter fails:** confirm tab context, re-apply valid filter payload, re-read content.
- **Profile action fails:** re-check profile context and current relationship state, then report exact tool failure text.
- **Messaging gate fails:** run `open_chat_window_of(user_name)` again, use new `page_id`, retry `send_messaging_message`.
- **Session/auth issue:** run `login`, then restart from the smallest necessary step.

## Best Practices

- Keep `page_id` ownership clear per workflow and reuse chat `page_id` for follow-ups.
- Personalize outreach only with observed profile evidence; mark unknowns explicitly.
- Use one clear CTA in outreach messages and avoid fabricated claims.
- Prefer dedicated LinkedIn tools over generic `run_javascript` when available.
- Return objective, tool sequence, `page_id` values, evidence, outcomes, unknowns, and next step.

## Examples

### Example 1: Prospect, filter, then connect

**User Request:** "Find SaaS founders in India and send one connection request."

**Approach:**
1. Run `search_people("founder saas india")` and capture `page_id`.
2. Run `get_page_content(page_id)` to list visible candidates.
3. Run `apply_filters(page_id, filter)` and re-read with `get_page_content(page_id)`.
4. Open selected profile with `open_page(profile_url)` and verify with `get_page_content`.
5. Send invite using `send_connection_request(profile_page_id, note)` and report exact outcome.

### Example 2: Message an existing connection

**User Request:** "Message Jane Doe, who is already in my connections."

**Approach:**
1. Run `search_person_in_my_connections("Jane Doe")` and review results via `get_page_content`.
2. Open chat once using `open_chat_window_of("Jane Doe")`.
3. Send initial note with `send_messaging_message(chat_page_id, message)`.
4. Send follow-up with the same `chat_page_id` and confirm tool success responses.
