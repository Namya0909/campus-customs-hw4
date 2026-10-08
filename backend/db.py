"""Shared SQLite connection helper for campus_customs.db."""

import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

# The data/ folder (campus_customs.db + products/) may sit in this folder or
# any parent (e.g. the repo root), same convention as the other homeworks.
DATA_DIR = None
for folder in (BACKEND_DIR, *BACKEND_DIR.parents):
    candidate = folder / "data"
    if (candidate / "campus_customs.db").exists():
        DATA_DIR = candidate
        break
if DATA_DIR is None:
    raise RuntimeError("Could not find a data/campus_customs.db in this folder or any parent.")

DB_PATH = DATA_DIR / "campus_customs.db"
PRODUCTS_DIR = DATA_DIR / "products"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
