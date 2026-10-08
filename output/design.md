# Visual Identity & UX Overhaul

A full pass over the site's look and feel, aimed at making Campus Customs read as an authentic, high-end collegiate storefront rather than a generic template. This documents every concrete change — what was touched, and why.

## Summary (as part of Problem 10)

First, we updated the store's visual identity by using deep Yale Blue, athletic heather grey, lots of white space, and warm gold accents. We added real Yale campus photos to hero banners and backgrounds to create an authentic atmosphere for Gen Z shoppers. This design highlights the prestige and energy of a high-end collegiate brand, helping build trust and encouraging visitors to spend more time exploring the store.

Next, we chose collegiate serif fonts for section headings and modern, easy-to-read sans-serif fonts for product descriptions and navigation. The site features smooth micro-interactions like soft drop-shadows on hover, fluid transitions, and gentle badge animations, making it feel responsive and tactile. A clear visual hierarchy helps users quickly scan categories and creates a sleek, dynamic shopping experience.

We also improved product presentation with high-contrast price tags, clear labels showing stock status, and edge-to-edge product photo cards. Clicking an item opens a split-view details page with high-resolution images and real-time size availability from the database. Showing stock information upfront helps customers avoid confusion about sizes and make faster checkout decisions.

Finally, we turned the floating chat widget into a luxury concierge service with Yale blue message bubbles, typing indicators, and smooth expand-and-collapse animations. When customers ask questions, the chatbot suggests apparel through interactive product cards right in the chat. This seamless connection between AI help and product discovery reduces cart abandonment and guides shoppers toward making a purchase.

## Typography

- **Headers**: [Playfair Display](https://fonts.google.com/specimen/Playfair+Display) (serif, weights 600/700/800) — loaded via Google Fonts in [index.html](../frontend/index.html). Applied globally to every `h1`–`h4` ([index.css](../frontend/src/index.css)), giving page titles ("About Campus Customs," "Products," the chat header) an academic, collegiate weight instead of looking like generic UI text.
- **Body**: [Inter](https://fonts.google.com/specimen/Inter) (sans-serif, weights 400–700) — set as the base `font-family` on `:root`, used for all paragraph copy, buttons, form fields, and nav.
- **Deliberate exception**: product card titles (`.product-info h3` in [Products.css](../frontend/src/pages/Products.css)) are explicitly kept in Inter, not Playfair — a decorative serif reads poorly at small sizes in a dense grid of 100+ cards. Serif is reserved for actual headings where it can breathe.

## Color hierarchy

Expanded the CSS custom-property palette in [index.css](../frontend/src/index.css):

| Variable | Value | Role |
|---|---|---|
| `--yale-blue` / `--yale-blue-dark` / `--yale-blue-light` | `#00356b` / `#001f3f` / `#286dc0` | Primary brand color — nav, hero, buttons, price tags. |
| `--heather` / `--heather-dark` / `--heather-tint` | `#8b93a1` / `#5c6473` / `#eef0f3` | Athletic heather grey — card borders on hover, the chat panel's message background, typing-indicator dots. |
| `--paper` / `--ink` / `--cloud` | `#fff` / `#1a1a1a` / `#f6f7f9` | Crisp white surfaces and near-black text, unchanged in spirit from before but the neutral grey (`--cloud`) was cooled slightly to sit better next to the new heather tones. |
| `--gold` / `--gold-dark` / `--gold-tint` | `#b9933f` / `#8f6f2b` / `#f6ead0` | **New** — used deliberately sparingly: the About page's title underline, the hero eyebrow text and secondary-button hover state, the chat bubble's left accent bar, and focus rings on the chat input. Never used for large fills — it's a highlight color, not a second primary. |

The result is a four-tier hierarchy (Yale Blue → heather grey → white → gold) instead of the old two-tone blue/white scheme, giving the site a sense of material hierarchy: blue for brand and primary action, grey for structure and secondary surfaces, gold for "this is a detail worth noticing."

## Micro-interactions

- **Product cards** ([Products.css](../frontend/src/pages/Products.css)): hover now lifts the card (`translateY(-5px)`), deepens the shadow, tints the border heather-grey, *and* zooms the photo itself (`scale(1.06)` on the image, clipped by `overflow: hidden`) — all on a shared `--ease-smooth` cubic-bezier for a consistent, non-linear feel instead of the flat `ease` timing used before.
- **Chat panel** ([ChatWidget.tsx](../frontend/src/components/ChatWidget.tsx) / [ChatWidget.css](../frontend/src/components/ChatWidget.css)): previously the panel was conditionally mounted/unmounted (`{isOpen && <div>...}`), so it could only ever pop in or out instantly — no transition is possible on an element that doesn't exist yet. It's now **always mounted** and toggled via a `chat-panel-open` class that animates `opacity`, `transform` (`translateY` + `scale`), and `visibility` together — a gentle modal-style entrance/exit instead of an instant appear. `visibility: hidden` (not `display: none`) is what makes the transition possible while still removing the panel from the tab order when closed (every interactive element inside also gets `tabIndex={-1}` while closed, so keyboard users can't tab into an invisible panel).
- **Buttons & nav** ([Home.css](../frontend/src/pages/Home.css), [NavBar.css](../frontend/src/components/NavBar.css), [AuthForm.css](../frontend/src/pages/AuthForm.css)): hover states now lift and deepen shadow on the same smooth easing curve; the active/hover nav underline changed from a flat light-blue to the new gold accent, so "where you are" in the nav reads as an intentional highlight rather than a default link color.

## Product presentation

- **High-contrast price tags**: price moved from plain inline text to a `.price-tag` pill (dark Yale-blue-on-white... actually white-on-dark-blue, with a drop shadow) defined once in `index.css` and reused everywhere a price appears: the Products grid (now an overlay badge on the top-right corner of the photo, like real e-commerce listings), the product detail page (a larger variant, `.price-tag-large`), and chat product cards. One visual language for price, instead of three separate ad-hoc styles.
- **Stock availability pills**: "In stock" / "Out of stock" went from plain colored text to an actual pill (`.stock-pill`) with a colored dot and a tinted background (soft green / soft red), again shared across the grid, the detail page's per-size table, and chat cards — scannable at a glance instead of reading as an afterthought label.
- **Crisper cards**: card corner radius increased slightly (12px → 14px), border color shifts to heather-grey on hover instead of just a shadow change, and the detail page's image panel gained a soft ambient shadow so it reads as a "mounted" photo rather than a flat rectangle.

## Concierge chat widget

- **Rebrand**: header copy changed from the generic "Campus Customs Assistant" to **"Campus Customs Concierge"** with a small circular avatar badge (🎓) and a subtitle ("Usually replies in a few seconds") — reads as a service, not a chatbot.
- **Branded bubbles**: assistant bubbles gained a left-edge gold accent bar (`border-left: 3px solid var(--gold)`) so a reply is identifiable at a glance even before reading it; user bubbles moved from flat Yale-blue to a subtle blue gradient. Both got a touch more border-radius and a soft shadow.
- **Typing feedback**: the old plain-text "Typing…" was replaced with a three-dot bouncing indicator (`.typing-dot`, staggered `animation-delay`, CSS `@keyframes`), the standard "someone is responding" pattern users already recognize from every modern messaging app.
- **Product cards inside chat** now use the same `.price-tag`/`.stock-pill` components as the rest of the site (previously they had their own separate, plainer styling) — one visual system for "this is a product" everywhere it appears.

## Photography

Three campus photographs were added, all **Carol M. Highsmith / Library of Congress donations — public domain, no license fee or attribution legally required** (credited anyway, as a matter of courtesy, in the hero's corner caption):

| Image | Used on | File |
|---|---|---|
| Cross Campus (Sterling Memorial Library facade across the lawn) | Home hero background, behind a Yale-blue gradient overlay for text contrast | `frontend/public/images/yale/cross-campus.jpg` |
| Harkness Tower | Home campus-photo strip; About page, beside the opening paragraph | `frontend/public/images/yale/harkness-tower.jpg` |
| Sterling Memorial Library (entrance) | Home campus-photo strip | `frontend/public/images/yale/sterling-library.jpg` |

These replace what was previously a flat gradient-only hero and an all-text About page with real, high-resolution architectural photography — the single biggest lever for the "ultra high-end, visually engaging" goal, and specifically the kind of photo-forward presentation that reads well to a Gen-Z audience scrolling quickly past a lot of flat, photo-less sites.

Each image was located via the Wikimedia Commons API (not guessed), its license metadata checked (`LicenseShortName: Public domain` for all three), and the file itself downloaded and visually reviewed before being committed to the repo.

## Files touched

`frontend/index.html`, `frontend/src/index.css`, `frontend/src/components/NavBar.css`, `frontend/src/components/ChatWidget.tsx`, `frontend/src/components/ChatWidget.css`, `frontend/src/pages/Home.tsx`, `frontend/src/pages/Home.css`, `frontend/src/pages/About.tsx`, `frontend/src/pages/About.css`, `frontend/src/pages/Products.tsx`, `frontend/src/pages/Products.css`, `frontend/src/pages/ProductDetail.tsx`, `frontend/src/pages/ProductDetail.css`, `frontend/src/pages/AuthForm.css`, plus three new images under `frontend/public/images/yale/`.

No backend changes were needed — this was a frontend/visual-only pass.
