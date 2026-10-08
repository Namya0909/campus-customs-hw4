# Campus Customs — Homework 4

A Yale-themed clothing shop: a React/Vite/TypeScript storefront backed by a FastAPI service,
with a PydanticAI shop-concierge chatbot that answers product, pricing, and stock questions
grounded in a live SQLite catalogue.

## Architecture

```
hw4/
├── frontend/            React + Vite + TypeScript storefront
├── backend/              FastAPI app + the PydanticAI agent
│   ├── main.py           FastAPI app: /api/products, /api/auth/*, /chat, /api/chat/history
│   ├── agent.py           Builds the PydanticAI Agent, loads prompts/prompt.md + model config,
│   │                      wires in dependency-injected customer identity/page context, and the
│   │                      output-grounding validator
│   ├── models.py          Pydantic types: chat contract, product cards, audit log entries
│   ├── tools.py           The agent's three DB-backed tools (search/detail/stock) + the
│   │                      category-normalization layer
│   ├── auth.py            Registration/login/session endpoints
│   ├── security.py        Password hashing (PBKDF2) + session token signing
│   ├── db.py              SQLite connection helper (resolves data/campus_customs.db)
│   ├── audit.py           Append-only audit logger → output/audit_trail.json
│   └── prompts/prompt.md  The agent's persona, tools guide, and safety guardrails
└── output/                Generated deliverables: harness.md (full architecture + test log),
                            design.md, usability.md, app_check.html (+ screenshots),
                            audit_trail.json (live agent activity log)
```

The frontend and backend are two independent processes — the frontend calls the backend over
HTTP (`VITE_API_URL`), there's no shared build step.

**Read [output/harness.md](output/harness.md) for the full architecture write-up** (data
models and why each field exists, the agent's tools, safety rules, and runtime settings like
model name, retry/result-cap limits, and session lifetime).

## Prerequisites

- Python 3.11+
- Node.js 18+
- A [Portkey](https://portkey.ai) API key (the agent's only external dependency)

## Local data pack

The product catalogue (`campus_customs.db`) and product photos are **not** committed to this
repo (see `.gitignore`) — they're provided separately as a data pack. After cloning, place it
at the repo root exactly like this:

```
hw4/
└── data/
    ├── campus_customs.db
    └── products/
        ├── some-product.jpg
        └── ... (all product photos)
```

The backend finds this automatically: `backend/db.py` searches its own folder and every parent
folder for `data/campus_customs.db`, so `hw4/data/` (one level above `backend/`) is exactly
where it looks first. If the data pack is missing, the backend will raise a clear error on
startup rather than silently serving nothing.

## Environment setup

Copy `.env.example` to **two** places and fill in real values — the backend and the frontend
each read their own `.env` independently (Vite never reads a parent folder's `.env`; the
backend does, but giving it its own keeps things unambiguous):

```bash
cp .env.example .env               # backend reads this (or backend/.env — see below)
cp .env.example frontend/.env      # frontend reads this one
```

- In the root/backend `.env`, set `PORTKEY_API_KEY` to a real key. `MODEL_NAME`,
  `PORTKEY_BASE_URL`, and `SESSION_SECRET` all have working defaults and only need to be
  uncommented/changed if you want something other than the default.
- In `frontend/.env`, set `VITE_API_URL` to match whatever port you run the backend on (the
  example below uses `http://localhost:8000`).

## Running the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r ../requirements.txt
uvicorn main:app --reload
```

This starts the FastAPI app on `http://localhost:8000` (uvicorn's default port). It serves:

- `GET /api/products`, `GET /api/products/{id}` — the catalogue
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `POST /chat` — the shop agent
- `GET /api/chat/history` — a logged-in customer's saved conversation

A pre-seeded test account exists in the data pack: **`test@campuscustoms.yale.edu`** /
**`password`**.

## Running the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

This starts the Vite dev server (prints its own URL, typically `http://localhost:5173` or
`5180` depending on what's free) — open that URL in a browser. Make sure `frontend/.env`'s
`VITE_API_URL` matches the port the backend actually printed in the step above.

## Verifying it's working

1. Open the frontend URL — you should see the Home page with a Yale campus photo hero.
2. Go to **Products** — the grid should populate from the backend; try the search/filter bar.
3. Open the chat widget (bottom-right) and ask something like *"what hoodies do you have?"* —
   it should reply with real product cards pulled from the database.
4. See [output/app_check.html](output/app_check.html) for screenshots of these checks already
   run against the live app, and [output/harness.md](output/harness.md) for the full test log.
