"""Database-backed tools for the Campus Customs chat agent.

Each tool queries campus_customs.db directly (via db.get_connection) and
returns Pydantic models from models.py, which the agent copies into its
structured ChatReply.
"""

import difflib
import json
import re
import sqlite3
from pathlib import Path

from db import get_connection
from models import ProductCard, ProductDetail, SizeAvailability, StockLookup

# A generous ceiling, not a real limit — the whole catalogue is ~100 items, so this only
# guards against a pathological max_results value, never against a legitimate category
# search. See search_products' docstring.
MAX_SEARCH_RESULTS = 100
DEFAULT_SEARCH_RESULTS = 50
SEARCHABLE_FIELDS = ["name", "description", "garment_type", "search_tags", "colors"]
FUZZY_MATCH_CUTOFF = 0.75

_vocabulary_cache: list[str] | None = None

# --- Category normalization -------------------------------------------------
#
# catalogue.garment_type is raw, uncurated text: "hoodie", "pullover hoodie", "hooded
# sweatshirt", and "full-zip hooded sweatshirt" are all the same thing to a shopper, but
# four different strings in the database. categorize() maps every product's name,
# description, and garment_type to one of four consistent, shopper-facing categories so
# "show me hoodies" (or the Products page's category dropdown) reliably groups all of them
# together instead of only matching one exact label.
#
# Kept in sync by hand with frontend/src/categories.ts's `categorize()` — same rules, same
# category labels — since the frontend and backend don't share code. If you change one,
# change the other.

SHOP_CATEGORIES = ["Hoodie", "T-Shirt", "Crewneck & Sweatshirt", "Jackets & Outerwear"]

_HOOD_RE = re.compile(r"\bhood(ie|ed)?\b")
_JACKET_RE = re.compile(r"\bjacket\b")
_SWEATSHIRT_RE = re.compile(r"\b(crewneck|crew-neck|sweatshirt|sweater|mockneck|quarter-zip|pullover)\b")
# "sweatshirt" itself contains the substring "tshirt" ("swea" + "tshirt"), so this exclusion
# check must use a word-bounded pattern, not a plain substring check.
_TSHIRT_HINT_RE = re.compile(r"\b(t-shirt|tshirt)\b")


def categorize(name: str, description: str, garment_type: str) -> str:
    """Map a product's free-text fields to one of SHOP_CATEGORIES."""
    text = f"{name} {description} {garment_type}".lower()

    if _HOOD_RE.search(text):
        return "Hoodie"
    if _JACKET_RE.search(text):
        return "Jackets & Outerwear"
    if _SWEATSHIRT_RE.search(text) and not _TSHIRT_HINT_RE.search(text):
        return "Crewneck & Sweatshirt"
    return "T-Shirt"


def _total_stock(conn: sqlite3.Connection, product_id: str) -> int:
    row = conn.execute(
        "SELECT COALESCE(SUM(quantity), 0) AS total FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchone()
    return row["total"]


def _size_availability_from_row(row: sqlite3.Row) -> SizeAvailability:
    return SizeAvailability(size=row["size"], quantity=row["quantity"], available=row["quantity"] > 0)


def product_card_from_row(conn: sqlite3.Connection, row: sqlite3.Row) -> ProductCard:
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        price=row["price"],
        image_url=f"/images/{Path(row['image_file_path']).name}",
        garment_type=row["garment_type"],
        in_stock=_total_stock(conn, row["product_id"]) > 0,
    )


def _catalogue_vocabulary(conn: sqlite3.Connection) -> list[str]:
    """Every distinct word that actually appears in the catalogue's searchable text.

    Built once per process and cached — used only to correct a search word that matched
    nothing, never to decide what a word "should" mean.
    """
    global _vocabulary_cache
    if _vocabulary_cache is not None:
        return _vocabulary_cache

    words: set[str] = set()
    rows = conn.execute("SELECT name, garment_type, search_tags, colors FROM catalogue").fetchall()
    for row in rows:
        words.update(row["name"].lower().split())
        words.update(row["garment_type"].lower().split())
        for phrase in json.loads(row["search_tags"]):
            words.update(phrase.lower().split())
        for phrase in json.loads(row["colors"]):
            words.update(phrase.lower().split())

    _vocabulary_cache = sorted(words)
    return _vocabulary_cache


def _correct_word(word: str, vocabulary: list[str]) -> str:
    """Best real catalogue word for a possibly-misspelled search word, or the word unchanged."""
    if len(word) < 4 or word in vocabulary:
        return word
    match = difflib.get_close_matches(word, vocabulary, n=1, cutoff=FUZZY_MATCH_CUTOFF)
    return match[0] if match else word


def _row_text(row: sqlite3.Row) -> str:
    return " ".join(row[field] for field in SEARCHABLE_FIELDS).lower()


def _row_matches_words(row: sqlite3.Row, words: list[str]) -> bool:
    """Every word must match the row's text OR its normalized category (AND across words)."""
    if not words:
        return True
    text = _row_text(row)
    category = categorize(row["name"], row["description"], row["garment_type"]).lower()
    return all(word in text or word in category for word in words)


def _row_in_price_range(row: sqlite3.Row, min_price: float | None, max_price: float | None) -> bool:
    if min_price is not None and row["price"] < min_price:
        return False
    if max_price is not None and row["price"] > max_price:
        return False
    return True


def search_products(
    query: str,
    max_results: int = DEFAULT_SEARCH_RESULTS,
    min_price: float | None = None,
    max_price: float | None = None,
) -> list[ProductCard]:
    """Search the catalogue by free-text keywords, optionally within a price range.

    Matches against product name, description, garment type, colors, search tags, AND each
    product's normalized shopping category (Hoodie, T-Shirt, Crewneck & Sweatshirt, Jackets &
    Outerwear — see categorize()). The category match is what makes a query like "hoodie"
    reliably return every hooded garment (pullover hoodie, hooded sweatshirt, full-zip hooded
    sweatshirt, ...), not just products whose raw garment_type happens to say "hoodie"
    literally. Every word in the query must match at least one of those fields or the
    category (in any field, any order), so e.g. "navy hoodie" only returns products that are
    both navy and a hoodie. If the exact words return nothing, each word is automatically
    corrected against real catalogue vocabulary (e.g. "hoddie" -> "hoodie") and the search is
    retried once.

    There is no artificial cap on how many results this can return beyond the full size of
    the catalogue — a category question should get every matching product, not just the
    first handful.

    Args:
        query: Free-text search terms, e.g. "navy hoodie", "Harvard shirt", "fleece jacket".
        max_results: Maximum number of products to return (default 50 — generous enough to
            cover any single category; raise it further if you ever need to).
        min_price: Only return products priced at or above this (e.g. for "nothing cheap").
        max_price: Only return products priced at or below this (e.g. for "under $70").
    """
    words = [w.strip().lower() for w in query.split() if w.strip()]
    if not words and min_price is None and max_price is None:
        return []
    limit = max(1, min(max_results, MAX_SEARCH_RESULTS))

    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        matches = [r for r in rows if _row_matches_words(r, words) and _row_in_price_range(r, min_price, max_price)]

        if not matches and words:
            vocabulary = _catalogue_vocabulary(conn)
            corrected = [_correct_word(w, vocabulary) for w in words]
            if corrected != words:
                matches = [
                    r for r in rows if _row_matches_words(r, corrected) and _row_in_price_range(r, min_price, max_price)
                ]

        return [product_card_from_row(conn, row) for row in matches[:limit]]
    finally:
        conn.close()


def get_product_details(product_id: str) -> ProductDetail | None:
    """Full details for one catalogue product: description, colors, and per-size stock.

    Args:
        product_id: Exact catalogue product_id, usually from a prior search_products result.
    """
    conn = get_connection()
    try:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None

        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (product_id,)
        ).fetchall()
        size_list = [_size_availability_from_row(s) for s in sizes]

        card = product_card_from_row(conn, row)
        return ProductDetail(
            **card.model_dump(),
            description=row["description"],
            colors=json.loads(row["colors"]),
            sizes=size_list,
        )
    finally:
        conn.close()


def check_stock(product_id: str, size: str | None = None) -> StockLookup:
    """Check exact stock for one product, broken down by every size it comes in.

    Always returns the full per-size breakdown, even when a specific size is requested, so
    you can point the shopper to an in-stock alternative size if the one they asked about is
    sold out. Every number comes straight from the inventory table — never estimate or round.

    Args:
        product_id: Exact catalogue product_id.
        size: A specific size to highlight (e.g. "L"), or omit to just list every size.
    """
    conn = get_connection()
    try:
        product = conn.execute("SELECT product_id FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if product is None:
            return StockLookup(product_id=product_id, found=False, requested_size=size)

        rows = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY id", (product_id,)
        ).fetchall()
        sizes = [_size_availability_from_row(r) for r in rows]
    finally:
        conn.close()

    requested_size_available = None
    if size:
        match = next((s for s in sizes if s.size.lower() == size.strip().lower()), None)
        requested_size_available = match.available if match is not None else False

    return StockLookup(
        product_id=product_id,
        found=True,
        requested_size=size,
        requested_size_available=requested_size_available,
        sizes=sizes,
    )
