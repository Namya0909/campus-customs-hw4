# Usability Improvements

Four improvements were selected from a shortlist of six (three frontend, three backend/agent options) — two per side. This file documents what was added and why it helps a Campus Customs shopper or the store.

## Summary (as part of Problem 9)

We started by adding a client-side search and filter bar in Products.tsx. It lets users search by keyword, pick garment types from a dropdown, filter for in-stock items, see the number of matching items instantly, and clear all filters with one button. Because it works on the already loaded catalogue and doesn't need extra network requests, shoppers can quickly find specific garments and check stock levels. This makes browsing easier and faster, helping customers discover items and improving catalog conversion.

Next, we improved ChatWidget.tsx by adding automatic scrolling for the message list and an unread message badge on the launcher. When new messages arrive, the chat window scrolls to the bottom. If a user closes or minimizes the chat while waiting for an LLM response, a red alert badge appears, thanks to a React ref that tracks the closed state during async requests. This keeps shoppers updated on new recommendations and helps them stay engaged, even if they're browsing other parts of the site.

We also updated the backend by adding typo-tolerant search to tools.py using Python's built-in difflib library, so there's no need for extra dependencies. If an exact search finds nothing, the search_products function tries again by correcting any misspelled words with the catalogue's vocabulary. This helps shoppers avoid empty results from small typos or mobile keyboard mistakes, so they can always see relevant products.

We also added budget-aware search to the search_products function by including min_price and max_price arguments, which map directly to SQL filters on catalogue.price. We updated prompt.md so the agent uses these parameters whenever a customer mentions a spending limit, like asking for gifts under $30. This way, price-sensitive recommendations are always based on real database prices, not LLM guesses, which keeps pricing accurate and gives customers clear, budget-friendly options.

## Frontend

### 1. Search & filter bar on the Products page

**What was added**: [Products.tsx](../frontend/src/pages/Products.tsx) now has a toolbar above the grid with a free-text search box (matches name/description), a garment-type dropdown (built from whatever types actually exist in the catalogue, so it never goes stale), and an "in stock only" checkbox. A live "X of 102" count and a "Clear filters" button (shown only when a filter is active) make the current state visible. Filtering happens client-side over the already-fetched catalogue — no new backend endpoint was needed.

**Why it helps**:
- **Shopper**: with 102 items and no way to narrow them down before, finding "a navy hoodie under the $70 range" meant scrolling and eyeballing every card. Now it's three inputs.
- **Store**: browsing friction is one of the most common reasons a visitor leaves without buying anything; this directly shortens the path from "landed on the Products page" to "found something."

### 2. Chat unread badge + auto-scroll

**What was added**: [ChatWidget.tsx](../frontend/src/components/ChatWidget.tsx) now auto-scrolls the message list to the newest message whenever the conversation changes or the panel opens (`messagesRef.scrollTo(...)` in a `useEffect`). Separately, if a reply arrives while the panel is closed (e.g. a shopper asked a question, then closed the widget before the assistant answered), a small red badge with a count appears on the floating chat button; opening the panel clears it.

**Why it helps**:
- **Shopper**: previously a reply could land silently — closed panel, or scrolled up reading an earlier message — and go unnoticed. Auto-scroll keeps the latest answer in view without a manual scroll; the badge makes sure a reply that arrives after the panel was closed is never just missed.
- **Store**: the whole point of Problem 7's product-card search results is lost if the shopper never actually sees them — this closes that gap.

## Backend / Agent

### 3. Typo-tolerant product search

**What was added**: [tools.py](../backend/tools.py)'s `search_products` now retries once, automatically, if the exact keyword search returns nothing: each search word is checked against a vocabulary built from the catalogue's own `name`/`garment_type`/`search_tags`/`colors` text (cached after the first build), using Python's stdlib `difflib.get_close_matches` (cutoff `0.75`, words under 4 characters skipped) to find the closest real catalogue word — "hoddie" → "hoodie", "crewnck" → "crewneck" — and re-runs the search with the corrected words. No new dependency was added.

**Why it helps**:
- **Shopper**: a typo or an unfamiliar spelling no longer dead-ends the conversation with "nothing matches" — the agent finds what was actually meant.
- **Store**: every "sorry, nothing matches" reply is a conversation that could have ended in a sale but didn't; this removes a whole class of them caused by nothing more than a misspelling.

### 4. Budget-aware search (price-range filtering)

**What was added**: `search_products` gained optional `min_price`/`max_price` parameters that translate directly into a `price >= ?` / `price <= ?` SQL filter against `catalogue.price` — not an estimate the model makes up. [prompt.md](../backend/prompts/prompt.md) now explicitly instructs the agent to use these for budget questions ("hoodies under $70", "between $40 and $60") instead of guessing from memory, and notes that a price range can be combined with an empty/generic keyword query too (e.g. just browsing "under $50").

**Why it helps**:
- **Shopper**: "what have you got under $70?" is one of the most natural real-shopping questions, and before this change the agent had no way to answer it with an exact, grounded number — it could only eyeball prices it happened to recall from an earlier tool call.
- **Store**: budget is often the actual deciding factor in a purchase; answering it precisely (rather than vaguely, or not at all) keeps a price-sensitive shopper in the conversation instead of having them leave to check prices themselves.

## Verified

| Feature | Test | Result |
|---|---|---|
| Search & filter bar | Typed "navy", picked "hoodie" from the type dropdown, checked "in stock only" | Count label and grid updated live; "Clear filters" appeared and reset all three controls |
| Chat badge + auto-scroll | Sent a message, closed the panel before the reply arrived | Badge appeared with count `1` on the toggle button; reopening cleared it and scrolled to the new reply |
| Typo-tolerant search | Chat: "do you have any hoddies?" | Returned 10 real hoodie products — same result as the correctly-spelled query |
| Budget-aware search | Chat: "Do you have any hoodies under $70?" | Replied "...priced under $70, all at $68.00" with 10 real products, all verified ≤ $70 |
