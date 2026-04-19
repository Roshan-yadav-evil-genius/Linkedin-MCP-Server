# LinkedIn MCP

**LinkedIn MCP** is a [Model Context Protocol](https://modelcontextprotocol.io/) server that connects an AI assistant to LinkedIn through a real browser session. The assistant can open pages, read what is on screen in plain text, run LinkedIn-focused actions (such as search and connection requests), and fall back to custom in-page actions when needed. Your sign-in state can be kept between sessions so repeat tasks do not always require logging in again.

## Who it is for

This project suits individuals or teams who want an AI agent to help with LinkedIn workflows—for example finding people, narrowing lists with filters, reading result pages, or taking simple actions on a member’s profile—while a human handles sign-in when LinkedIn asks for it (password, second factor, or other checks).

## How the agent typically works

1. **Sign in when needed** — The assistant can start an interactive sign-in flow. You complete authentication in the browser; when you close the window, the saved session is ready for later steps.
2. **Work on a specific page** — The assistant opens a URL and receives a short-lived **tab reference** for that page. Most tools expect the right kind of LinkedIn page to be active on that tab (for example a person’s profile or people search results).
3. **Act or read** — The assistant can run built-in LinkedIn actions (connect, follow, search, filters, pagination) or **read the current page as clean text** so it can reason over names, headlines, and snippets. For unusual layouts, it can run **custom actions inside the page** when the built-in tools are not enough.
4. **Close when finished** — The assistant can close tabs it no longer needs so work stays tidy.

## Capabilities

### Session and browsing

- **Interactive sign-in** — Open a real browser so you can log in or refresh your session; state is saved for future automation.
- **Open and close pages** — Navigate to a URL on a tracked tab, or close a tab when done.
- **Read page content** — Get the visible content of the current tab as readable text (suitable for the model to analyze).
- **Custom in-page actions** — Run tailored logic inside the active tab when you need behavior that is not covered by the built-in LinkedIn tools.

### Member profile (profile must be the active tab)

- **Send a connection request** — Optionally include a short personalized note, or send without a note when the site allows it.
- **Withdraw a pending request** — Cancel an outbound invitation that is still pending.
- **Follow the member** — Subscribe to their public updates without necessarily connecting.
- **Unfollow the member** — Stop following their updates.

### People discovery and lists

- **Search people (broad)** — Open LinkedIn people search for keywords such as title, company, or skills.
- **Search within your first-degree network** — Open a people view scoped to your existing connections (or the closest equivalent search experience).
- **Apply filters** — Narrow people results by relationship degree, people connected to a named member, or followers of a named member (when the filter UI supports it).
- **Next or previous page of results** — Move through paginated people search results.

Search and filter tools **change what is on screen**; the assistant should **read the tab** afterward if it needs to list names, compare candidates, or summarize the page.

## What changes the site vs what only reads

| Changes LinkedIn (mutating) | Reads only |
|----------------------------|------------|
| Send or withdraw a connection request; follow or unfollow | Read tab content as text |
| Open people search or connections-scoped search | Use the same read step after the page loads |
| Apply search filters; go to next or previous results page | |
| Custom in-page actions that click, type, or submit | Custom in-page actions used only to gather text from the page |

Built-in search tools **open** the right view and return a message that includes a tab reference; they do **not** return the full result list by themselves. After the page updates, the assistant uses the read capability on that tab to see results.

## Example flows (what an agent can do)

1. **Discover and narrow candidates** — Run a people search for your keywords, optionally apply filters (for example second-degree only), move to the next page if needed, and read each view so it can summarize or shortlist profiles.
2. **Connect from a profile** — Open the member’s profile, send a connection request with a short note you approve, or send without a note when appropriate.
3. **Clean up an invitation** — Open the member’s profile and withdraw a pending request if plans change.
4. **Stay in touch without connecting** — Open a profile and follow (or unfollow) public updates.

## Expectations and limits

LinkedIn’s interface and rules change over time; a flow that worked yesterday may need adjustment. Accounts can hit limits or see controls disabled (for example already connected, invite pending, or messaging restrictions). Some filters or buttons may not appear for every account or locale.

Use automation responsibly: respect LinkedIn’s terms of service, applicable laws, and courteous outreach. This README is not legal advice; you are responsible for how you use the tools.

## For contributors

Implementation and selector architecture are described in [CoreArchitecture.md](CoreArchitecture.md).
