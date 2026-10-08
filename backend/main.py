"""Campus Customs backend API.

Serves the product catalogue (from campus_customs.db) and the product photos
(from data/products/) to the React frontend, and runs the PydanticAI shop
chatbot behind POST /chat.

Usage (from inside backend/):
    uvicorn main:app --reload --port 8000
"""

import json
import sqlite3
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from agent import run_chat
from auth import UserOut, get_optional_current_user
from auth import router as auth_router
from db import PRODUCTS_DIR, get_connection
from models import ChatHistoryEntry, ChatReply, ChatRequest, ProductCard
from tools import product_card_from_row

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180", "http://127.0.0.1:5180"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/images", StaticFiles(directory=PRODUCTS_DIR), name="images")
app.include_router(auth_router)


def row_to_product(row: sqlite3.Row, inventory: list[dict]) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": f"/images/{Path(row['image_file_path']).name}",
        "price": row["price"],
        "inventory": inventory,
    }


@app.get("/api/products")
def list_products():
    """All catalogue items plus their size/quantity inventory."""
    conn = get_connection()
    try:
        products = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        inventory_rows = conn.execute(
            "SELECT product_id, size, quantity FROM inventory"
        ).fetchall()
    finally:
        conn.close()

    inventory_by_product: dict[str, list[dict]] = {}
    for inv in inventory_rows:
        inventory_by_product.setdefault(inv["product_id"], []).append(
            {"size": inv["size"], "quantity": inv["quantity"]}
        )

    return [row_to_product(p, inventory_by_product.get(p["product_id"], [])) for p in products]


@app.get("/api/products/{product_id}")
def get_product(product_id: str):
    """A single catalogue item plus its size/quantity inventory."""
    conn = get_connection()
    try:
        product = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")

        inventory = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()
    finally:
        conn.close()

    return row_to_product(product, [{"size": i["size"], "quantity": i["quantity"]} for i in inventory])


def _save_chat_turn(conn: sqlite3.Connection, user_id: int, role: str, content: str, products: list[ProductCard]) -> None:
    conn.execute(
        "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
        (user_id, role, content, json.dumps([p.model_dump() for p in products])),
    )


@app.post("/chat", response_model=ChatReply)
async def chat(body: ChatRequest, user: UserOut | None = Depends(get_optional_current_user)):
    """Runs the customer's message through the PydanticAI shop agent.

    Guests (no session cookie) get a reply but nothing is saved. Logged-in customers get their
    name/email passed into the agent for personalization, and both turns of this exchange are
    saved to chat_messages so the conversation reloads the next time they log in.
    """
    try:
        reply = await run_chat(
            body.message,
            body.history,
            customer_name=user.first_name or user.name if user else None,
            customer_email=user.email if user else None,
            page_context=body.page_context,
        )
    except RuntimeError as exc:
        # e.g. PORTKEY_API_KEY not set — a configuration problem, not a bad request.
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Chat agent failed: {exc}") from exc

    if user is not None:
        conn = get_connection()
        try:
            _save_chat_turn(conn, user.id, "user", body.message, [])
            _save_chat_turn(conn, user.id, "assistant", reply.message, reply.products)
            conn.commit()
        finally:
            conn.close()

    return reply


@app.get("/api/chat/history", response_model=list[ChatHistoryEntry])
def chat_history(user: UserOut | None = Depends(get_optional_current_user)):
    """The logged-in customer's saved conversation, oldest first. 401 for guests (nothing is saved for them)."""
    if user is None:
        raise HTTPException(status_code=401, detail="Log in to load saved chat history.")

    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id",
            (user.id,),
        ).fetchall()

        entries = []
        for row in rows:
            products: list[ProductCard] = []
            for item in json.loads(row["products_json"] or "[]"):
                product_id = item.get("product_id") if isinstance(item, dict) else None
                if not product_id:
                    continue
                # Re-fetch from the catalogue rather than trusting the stored snapshot, so a
                # price/stock change — or a products_json shape saved by an older version of
                # this app — can't resurface as stale or malformed data.
                catalogue_row = conn.execute(
                    "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
                ).fetchone()
                if catalogue_row is not None:
                    products.append(product_card_from_row(conn, catalogue_row))
            entries.append(ChatHistoryEntry(role=row["role"], content=row["content"], products=products))
    finally:
        conn.close()

    return entries
