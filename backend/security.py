"""Password hashing and session-token helpers.

Password format stored in users.password_hash:
    pbkdf2_sha256$<salt>$<hex digest>

This matches the pre-seeded rows in campus_customs.db (PBKDF2-HMAC-SHA256,
120,000 iterations, 32-byte digest, salt used as raw UTF-8 bytes) — new
registrations use the same scheme so old and new accounts log in the same way.
"""

import hashlib
import hmac
import os
import secrets
import time
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
# The .env may sit in this folder or any parent (e.g. the repo root).
for folder in (BACKEND_DIR, *BACKEND_DIR.parents):
    load_dotenv(folder / ".env", override=False)

PBKDF2_ITERATIONS = 120_000
PBKDF2_DKLEN = 32

SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-only-insecure-secret-change-me")
SESSION_TTL_SECONDS = 7 * 24 * 3600  # 7 days


def hash_password(password: str) -> str:
    salt = secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS, dklen=PBKDF2_DKLEN
    )
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        scheme, salt, hex_digest = stored_hash.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False

    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS, dklen=PBKDF2_DKLEN
    )
    return hmac.compare_digest(candidate.hex(), hex_digest)


def create_session_token(user_id: int) -> str:
    """A signed, expiring token: '<user_id>.<expiry>.<hmac signature>'."""
    expires_at = int(time.time()) + SESSION_TTL_SECONDS
    payload = f"{user_id}.{expires_at}"
    signature = hmac.new(SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{payload}.{signature}"


def verify_session_token(token: str) -> int | None:
    """Returns the user_id if the token is well-formed, unexpired, and unmodified."""
    try:
        user_id_str, expires_at_str, signature = token.split(".")
    except ValueError:
        return None

    payload = f"{user_id_str}.{expires_at_str}"
    expected_signature = hmac.new(
        SESSION_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(signature, expected_signature):
        return None

    if int(expires_at_str) < time.time():
        return None

    return int(user_id_str)
