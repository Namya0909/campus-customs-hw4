# Homework 4 — AI Prompt Log

Prompt log for the "vibe coding" portions of Homework 4. For each problem, this records the initial prompt, a follow-up prompt if one was needed, and a single sentence on what was lacking after the first prompt that led to the follow-up.

---

## Problem 1: AI Prompt Log Setup

### Initial Prompt
```
I am doing HW4, for section 1 of it - create an AI_prompts.md file in the homework 4 folder
which will serve as the prompt log for Homework 4. It should have clean markdown headings for
vibe coder prompts, including placeholders for each problem's title, the initial prompt I
typed, a follow-up prompt if needed, and a single sentence explaining what was lacking after
the first prompt that led to the second prompt.
```

### Follow-up Prompt (if needed)
No follow-up was needed — the template (headings, placeholders, structure) matched what was asked for on the first attempt.

### What was lacking
Nothing — this was a one-shot scaffolding task with no code to get wrong.

---

## Problem 2: Understanding the Campus Customs Database

### Initial Prompt
```
Now for section 2, I need to understand the db- can you show me the database for campus
catalogues so that I can understand the fields
```

### Follow-up Prompt (if needed)
```
Now, also mention each table and all its fields and why each filed is important for the shop
or for the chatbot in the output/harness.md
```
(Earlier in the same section, the user also supplied the real `campus_customs.db` + product
images as a zip, and separately asked to scaffold `output/harness.md` with a small table before
this expansion request.)

### What was lacking
The first pass only explained the schema in chat and gave `harness.md` a bare placeholder test table — it didn't yet document every table's fields with the "why it matters to the shop/chatbot" rationale the user actually wanted captured in the deliverable file.

---

## Problem 3: React/Vite Frontend + FastAPI Backend Scaffold

### Initial Prompt
```
Great!!!! Now for section 3, we need to build the frontend and some part of the backend using
React, Vite, and TypeScript. Use the Yale Bulldog website- https://yalebulldogblue.com/
website as reference but do not copy it word to word. Implement a top navigation bar with
links to Home, Products, About Us, Log in, and Create account, and provide original Campus
Customs-style copy in our voice for the Home and About Us sections. On the Products page,
render a catalogue grid pulling data from our SQLite database via a new /api/products FastAPI
endpoint in backend/main.py, serving the product photos from data/products/ and showing each
item's name, price, short description, and thumbnail. Enable single-item product views so that
clicking an item card navigates to a detailed product page with a split layout that features a
large image on one side and the full description, price, and size/stock availability on the
other. Finally, add a floating chat widget placed in the bottom-right corner of the site with
an interactive open/close panel and a stubbed message handler ready to connect to our backend
agent in upcoming steps.
```

### Follow-up Prompt (if needed)
No follow-up was needed — the spec was detailed enough (exact nav items, exact endpoint name, exact layout) to implement end-to-end in one pass, verified via `tsc`, `vite build`, and `curl` against the new endpoint.

### What was lacking
Nothing in the implementation itself; the only real snag was environmental (an unrelated process already using the "obvious" ports 8000/5173 on this machine), which was a local port conflict, not a gap in the prompt.

---

## Problem 4: Account Creation & Login

### Initial Prompt
```
Now for Problem 4, we need to implement the complete account creation and login flow. On the
FastAPI backend, set up registration and login endpoints that interact with the users table in
data/campus_customs.db, capturing first name, last name, full name, email, and securely hashed
passwords using pbkdf2_sha256 so it remains fully compatible with the existing test user
credentials (test@campuscustoms.yale.edu with password password). On the React frontend, build
and hook up the Create Account and Log In forms with proper validation, including first name,
last name, email, password, and a confirm-password field during signup, and verify that both
the pre-seeded test user and a newly registered account can log in smoothly (produce the test
result summary for me to review). Finally, update output/harness.md with an authentication
section explaining what fields we store for a user, how sessions are handled, and how the
password hashing strategy protects credentials against unauthorized access.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing — the exact PBKDF2 parameters (salt handling, iteration count) were reverse-engineered from the seeded test user's existing hash before writing any registration code, so new and pre-seeded accounts were compatible on the first attempt.

---

## Problem 5: PydanticAI Shop Chatbot Agent

### Initial Prompt
```
Awesome, so now for problem 5, we need to build the shop chatbot as a PydanticAI agent running
behind FastAPI in backend/main.py and connect it to our frontend chat widget. Inside the
backend/ directory, organise the agent into four distinct files: 1. backend/prompts/prompt.md
containing the Campus Customs store persona, tone, and foundational safety rules 2. agent.py
for agent initialization and loading the system prompt and LLM model via our API key 3.
tools.py for database query tools and 4. models.py defining Pydantic types for chat requests,
structured replies, and product card payloads. In backend/main.py, expose a /chat endpoint
that processes incoming user messages through the PydanticAI agent and returns both the
conversational response and matched product data. Ensure the FastAPI application can run
cleanly from inside backend/ using uvicorn main:app --reload --port 8000. Finally, update
output/harness.md with documentation on how the React frontend communicates with the FastAPI
chat route and how the PydanticAI agent loads its prompt file and model configuration.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing in the design itself; the only caveat noted back to the user was environmental — port 8000 was already occupied by an unrelated process on this machine, so local verification ran on a different port while the code/docs kept 8000 as the documented default.

---

## Problem 6: Database Query Tools for the Agent

### Initial Prompt
```
Okay the! Now for problem 6, we need to add database query functions to the chatbot agent so
that it can give accurate and reliable information about products, including details and stock
levels. In the file backend/tools.py, create tools for the PydanticAI agent to query the
campus_customs.db database for product descriptions, exact prices, and the stock levels broken
down by size as provided in the inventory table. Make sure that the agent never makes up
prices or inventory amounts and that it clearly informs the shopper when a particular size is
unavailable. Update the file backend/models.py by adding structured return types for these
tool queries, and expand the file backend/prompts/prompt.md with clear instructions telling
the agent to use these lookup tools each time a user asks about product specifications, costs,
or the availability of a size. Finally, updte the file output/harness.md by including a list of
each tool and by explaining the model fields that have been selected for the lookup results and
the reasons for this choice.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing was missing from the prompt; while implementing it, a self-caught gap was fixed proactively (not prompted by the user) — the original grounding check only verified a tool had *ever* been called, so it was strengthened to require a lookup tool call in that same turn before trusting any product claim.

---

## Problem 7: Chat-Driven Product Search UI

### Initial Prompt
```
Great! So now for problem 7 we need to implement the chat-driven product search feature that
dynamically updates the website UI. In the backend, establish the API contract so that when a
shopper asks about a category or type of item (such as "what hoodies do you have?"), the
PydanticAI agent queries the catalogue and returns structured product matches alongside its
textual reply. On React frontend, listen for these structrud product payloads from chat
responses and dynamically render them as product cards showing image, name, price, and brief
details, ensuring that clicking any card opens detailed single-item split view built in
probelm 3. In backend/prompts/prompt.md, instruct the agent to return matched items whenever
category searches occur, and update output/harness.md to document the exact API contract
explaining how search results flow from the agent to the frontend UI.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing — most of the groundwork already existed from Problems 5–6, so this prompt mainly needed a few closing touches (a "brief details" line on chat cards, stronger category-search prompt wording, and an honesty fix so the agent didn't claim a "full selection" when results were capped), all handled in the same pass.

---

## Problem 8: Customer Memory & Page Context

### Initial Prompt
```
Okay the! Now for problem 8 we need to implement customer memory and page context so that the
chatbot recognises returning shoppers and understands what they are viewing on screen. On the
backend, make sure that each time an authenticated customer chats, their conversation turns and
any associated product data are saved to the database's chat_messages table and automatically
reloaded into the frontend chat interface when they log back in, while allowing guest shoppers
to chat without saving history. Pass customer identity details, specifically their name and
email, into the PydanticAI agent's dependencies or context tools so that the agent is able to
personalise its replies. Moreover, update the chat request payload from the React frontend to
include the current page context (for example, the active product_id and the item title when a
customer is viewing a single-item detail page), in order that the agent can properly answer
questions that are based on the context such as "do you have this in blue?". Finally, document
in the output/harness.md file how the chat messages are stored, what customer fields the agent
can access, and how the frontend page context is injected into the agent run.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing in the prompt itself; one real bug was found and fixed during implementation (not via a user follow-up) — the pre-seeded demo chat history used an older `products_json` shape that didn't match the current `ProductCard` schema, so `GET /api/chat/history` was changed to re-fetch each product from the catalogue by `product_id` instead of trusting the stored snapshot.

---

## Problem 9: Usability Improvements

### Initial Prompt
```
Now for problem 9, we need to implement usability improvements across the site and chatbot
with exactly two for the front end and two for the agent or backend. Before coding, please
provide me with three strong options for the front end and three options for the backend,
explaining what each does and how it benefits either the customer or the business, so I can
review them and choose which specific features to implement. Once I select the final four,
help me write up output/usability.md with what was added and why it helps a Campus Customs
shopper or the store, and then guide me through implementing them cleanly into the running
application.
```

### Follow-up Prompt
```
So, right now, the garment type dropdown pulls raw, unnormalized strings from the database.
This leads to entries like "Hoodie", "Pullover Hoodie", "Hooded Sweatshirt", "Full-Zip Hooded
Sweatshirt", and "Hooded Pullover Sweatshirt", along with similar duplicates for t-shirts,
crewnecks, and jackets. Because of this, choosing "Hoodie" only shows the 5 items labeled
exactly as "Hoodie" instead of all 26 hooded garments. It also makes it hard for the agent to
count categories accurately.

To fix this, add a category normalization layer on both the frontend (Products.tsx) and
backend (backend/tools.py). This layer should map each product's title, description, and raw
type to clear, high-level shopping categories. For example, 'Hoodie' should match any product
with 'hoodie', 'hooded', or 'hood' in its details, so all 26 hooded items are grouped
together. Other products should be sorted into standard categories like 'T-Shirt', 'Crewneck
& Sweatshirt', and 'Jackets & Outerwear'.

Next, update the dropdown menu in Products.tsx to show only these cleaned-up categories. When
someone selects "Hoodie", the counter should update to "26 of 102" and display all 26 matching
products. In backend/tools.py and prompt.md, make sure search_products uses the same keyword
matching for titles, descriptions, and categories, and does not limit results to just 10
items. This way, the chatbot can always find and show all 26 hoodies when customers ask.
```

### What was lacking
The first pass at the search/filter bar filtered the dropdown on the catalogue's raw `garment_type` string with exact equality and capped `search_products` at 10 results, so near-duplicate labels for the same real-world category (e.g. "hoodie" vs. "pullover hoodie" vs. "hooded sweatshirt") were never grouped together — selecting "Hoodie" or asking the chatbot for hoodies only ever surfaced a fraction of what the store actually carried (5–10 of the true 27).

---

## Problem 10: Visual Identity & UX Overhaul

### Initial Prompt
```
Now for Problem 10, we need to overhaul the visual identity and user experience across the
site so it feels like an authentic, very engaging and ultra high-end Campus Customs collegiate
storefront. Update the typography with refined collegiate headers and clean body fonts,
establish an intentional color hierarchy anchored by Yale Blues, athletic heather grey, crisp
white, and subtle gold accents, and introduce smooth micro-interactions such as card hover
elevations and gentle modal transitions. Elevate the product presentation with crisp
photography cards, high-contrast price tags, clear stock availability pills, and refine the
bottom-right floating chat panel into an integrated, modern concierge widget with branded
bubbles and typing feedback. Also add free stock images from yale to the website to make it
more visually appealing especially for the genz. Finally, generate output/design.md where I can
detail the concrete visual and UX changes made.
```

### Follow-up Prompt (if needed)
```
now to design.md add this writeup which details the updates made in problem 10: [the user's
own four-paragraph summary of the typography/color/micro-interaction/concierge-widget work]
```
followed by a small tweak: `pls do mention "as part of problem 10" next to summary`.

### What was lacking
The implementation itself was complete on the first pass (verified via `tsc`/`vite build` and three real, license-checked Yale campus photos); the follow-ups were about adding the user's own written narrative summary into `design.md` rather than fixing anything that was built incorrectly.

---

## Problem 11: Live App Check (`output/app_check.html`)

### Initial Prompt
```
Now for Problem 11, we need to test the live running site and document the results in
output/app_check.html so a grader can double-click and review it directly. Please create the
output/app_check.html file using a clean, readable layout where each test check has a clear
heading, an embedded screenshot image, and one to two sentences explaining what the screenshot
proves. We need three test cases documented: 1. The chat checking the inventory level of an
item with honest stock and price pulled from the database; second 2. the dynamic search-result
product cards appearing in the chat or on-screen after asking a category question like "show me
hoodies"; and 3. One of the usability features we built in Problem 9, such as the real-time
client-side filter and count bar on Products.tsx or the unread message alert badge on
ChatWidget.tsx. Create output/app_check_images/ and save all captured screenshot image
files(for example, app_check_images/inventory.png, app_check_images/search_cards.png, and
app_check_images/usability_filter.png) and reference them using relative paths inside
app_check.html.
```

### Follow-up Prompt (if needed)
The user supplied the three actual screenshots (webp files) after being told screenshots couldn't be captured in this environment, with the instruction to place them as `inventory.png`, `search_cards.png`, and `usability_filter.png`.

### What was lacking
This environment has no working in-app browser preview and no connected Chrome extension, so the first pass could only ship the page's layout with placeholder boxes where screenshots would go — the user's follow-up with real screenshots was required to complete the deliverable, after which the write-up text was updated to quote the screenshots verbatim.

---

## Problem 12: Audit Trail & Safety Guardrails

### Initial Prompt
```
Now for Problem 12, we need to set up an audit trail, apply the agent's safety rules, and
finish the architecture documentation in output/harness.md. On the backend, add an append-only
logging system that saves the agent's loop activity in output/audit_trail.json. This log should
keep all previous entries between runs and for each tool execution or turn, include timestamp,
tool name, shortened arguments and results, and the stop reason. Next, define clear safety
guardrails in prompts/prompt.md to stop prompt injection, prevent unauthorized price changes or
false discounts, limit off-topic conversations, and require polite refusals if policies are
broken. Finaly update output/harness.md with a straightforward architectural summary. This
should explain the data models & fields in models.py and why they was chosen, list the agent's
tools and features, describe the safety rules, and outline runtime details like loop limits,
result caps, model settings, and instructions for starting both the frontend and backend.
```

### Follow-up Prompt (if needed)
No follow-up was needed.

### What was lacking
Nothing — all four guardrail categories (prompt injection, pricing integrity, off-topic limiting, polite refusals) were verified live against the running agent with real adversarial-style prompts, and the audit log was verified end-to-end including a genuine error-path capture (a blunt injection attempt rejected by the model provider's own content filter).

---

## Problem 13: Packaging & GitHub Submission

### Initial Prompt
```
Now for Problem 13, we need to prepare our entire codebase inside a clean hw4 folder and push
it to a public GitHub repository for submission. First, ensure our .gitignore strictly excludes
our active .env file, the local database (campus_customs.db), and local product image assets
(data/ and products/), and create a .env.example in the root containing only placeholder
environment keys (no actual API keys pls). Next, write a comprehensive README.md that explains
the project architecture, specifies exactly where a grader must place the local data pack
(campus_customs.db and product images) after cloning, details how to set up environment keys,
and provides explicit step-by-step commands to run both the FastAPI backend (uvicorn main:app
--reload) and Vite React frontend (npm run dev). Finally, verify that our local directory
layout precisely matches the assignment file tree, the picture has been attached. Provide the
exact terminal commands to inspect git status, stage and commit all required files without
leaking sensitive data or database binaries, and push to a public main branch.
```

### Follow-up Prompt (if needed)
```
actually you do it
```

### What was lacking
The first response deliberately stopped short of actually creating the GitHub repo and pushing — a public push is a consequential, externally-visible action, so it was held for explicit confirmation (and the user was asked which repo/approach to use) rather than assumed; the follow-up ("actually you do it") supplied that authorization, after which the repo was created and pushed.
