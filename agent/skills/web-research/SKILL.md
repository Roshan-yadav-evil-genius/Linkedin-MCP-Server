---
name: web-research
description: Execute browser-backed web research using deterministic open-read-act-verify loops. Use when the user asks to open webpages, extract visible page evidence, navigate tabs, run targeted JavaScript, or recover browser session/authentication before continuing research.
---

# Web Research

## Overview

Use this skill for generic browser/session/page workflows backed by `server.py` tools. Prioritize reliable extraction by reading page state before and after any action, and keep reporting tied to observed evidence.

## Instructions

### Step 1: Run a deterministic execution loop
1. **Pre-flight:** define objective, target URL, and required evidence fields.
2. **Acquire tab:** call `open_page(url)` (or reuse a valid existing `page_id`).
3. **Read state:** call `get_page_content(page_id)` and confirm destination/content.
4. **Act if needed:** use `run_javascript(page_id, script)` only for targeted gaps.
5. **Re-verify:** call `get_page_content(page_id)` again and compare expected vs actual.
6. **Cleanup:** call `close_page(page_id)` for tabs no longer needed.

### Step 2: Prefer strong tool hygiene
- Save and track every `page_id`.
- Keep one active tab per objective where possible.
- Make JavaScript minimal and return values for clear reporting.
- Prefer dedicated domain tools (for example LinkedIn-specific tools) over generic JavaScript when available.

### Step 3: Apply failure recovery paths
- **Invalid/closed `page_id`:** reopen via `open_page`, then re-read with `get_page_content`.
- **JavaScript error:** simplify script, re-check page state, and switch to dedicated tool path if possible.
- **Session/auth failure:** run `login`, reopen target page, and resume from read/verify steps.

## Best Practices

- Extract only task-critical fields and mark missing values as `unknown` instead of inferring.
- Never claim success without a verifying read or explicit success string.
- Separate observed evidence from assumptions in outputs.
- Stop repeating identical failing calls; change approach after each failure.
- Return objective, `page_id` used, ordered tools called, evidence, unknowns, and next step.

## Examples

### Example 1: Research one target page

**User Request:** "Open this company page and extract mission, pricing, and contact details."

**Approach:**
1. Run `open_page(url)` and store the returned `page_id`.
2. Run `get_page_content(page_id)` and extract mission/pricing/contact fields.
3. If content needs expansion (for example hidden sections), run focused `run_javascript(page_id, script)`.
4. Run `get_page_content(page_id)` again to verify extracted fields.
5. Report evidence and unknowns, then `close_page(page_id)` when done.

### Example 2: Recover from session failure

**User Request:** "The page keeps failing due to auth state; continue the research."

**Approach:**
1. Run `login` to refresh authenticated browser state.
2. Reopen target URL with `open_page(url)`.
3. Resume the read-act-verify loop with `get_page_content`, optional `run_javascript`, and final verification.
---
name: web-research
description: Execute browser-backed web research using deterministic open-read-act-verify loops. Use when the user asks to open webpages, extract visible page evidence, navigate tabs, run targeted JavaScript, or recover browser session/authentication before continuing research.
---

# Web Research

## Overview

Use this skill for generic browser/session/page workflows backed by `server.py` tools. Prioritize reliable extraction by reading page state before and after any action, and keep reporting tied to observed evidence.

## Instructions

### Step 1: Run a deterministic execution loop
1. **Pre-flight:** define objective, target URL, and required evidence fields.
2. **Acquire tab:** call `open_page(url)` (or reuse a valid existing `page_id`).
3. **Read state:** call `get_page_content(page_id)` and confirm destination/content.
4. **Act if needed:** use `run_javascript(page_id, script)` only for targeted gaps.
5. **Re-verify:** call `get_page_content(page_id)` again and compare expected vs actual.
6. **Cleanup:** call `close_page(page_id)` for tabs no longer needed.

### Step 2: Prefer strong tool hygiene
- Save and track every `page_id`.
- Keep one active tab per objective where possible.
- Make JavaScript minimal and return values for clear reporting.
- Prefer dedicated domain tools (for example LinkedIn-specific tools) over generic JavaScript when available.

### Step 3: Apply failure recovery paths
- **Invalid/closed `page_id`:** reopen via `open_page`, then re-read with `get_page_content`.
- **JavaScript error:** simplify script, re-check page state, and switch to dedicated tool path if possible.
- **Session/auth failure:** run `login`, reopen target page, and resume from read/verify steps.

## Best Practices

- Extract only task-critical fields and mark missing values as `unknown` instead of inferring.
- Never claim success without a verifying read or explicit success string.
- Separate observed evidence from assumptions in outputs.
- Stop repeating identical failing calls; change approach after each failure.
- Return objective, `page_id` used, ordered tools called, evidence, unknowns, and next step.

## Examples

### Example 1: Research one target page

**User Request:** "Open this company page and extract mission, pricing, and contact details."

**Approach:**
1. Run `open_page(url)` and store the returned `page_id`.
2. Run `get_page_content(page_id)` and extract mission/pricing/contact fields.
3. If content needs expansion (for example hidden sections), run focused `run_javascript(page_id, script)`.
4. Run `get_page_content(page_id)` again to verify extracted fields.
5. Report evidence and unknowns, then `close_page(page_id)` when done.

### Example 2: Recover from session failure

**User Request:** "The page keeps failing due to auth state; continue the research."

**Approach:**
1. Run `login` to refresh authenticated browser state.
2. Reopen target URL with `open_page(url)`.
3. Resume the read-act-verify loop with `get_page_content`, optional `run_javascript`, and final verification.
