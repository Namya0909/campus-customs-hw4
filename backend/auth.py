"""Registration, login, logout, and session-check endpoints."""

import sqlite3

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field

from db import get_connection
from security import create_session_token, hash_password, verify_password, verify_session_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

SESSION_COOKIE_NAME = "cc_session"


class RegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str | None
    last_name: str | None
    name: str
    email: str


def row_to_user(row: sqlite3.Row) -> UserOut:
    return UserOut(
        id=row["id"],
        first_name=row["first_name"],
        last_name=row["last_name"],
        name=row["name"],
        email=row["email"],
    )


def set_session_cookie(response: Response, user_id: int) -> None:
    token = create_session_token(user_id)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600,
        path="/",
    )


@router.post("/register", response_model=UserOut, status_code=201)
def register(body: RegisterRequest, response: Response):
    email = body.email.lower()
    full_name = f"{body.first_name.strip()} {body.last_name.strip()}".strip()
    password_hash = hash_password(body.password)

    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")

        cursor = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, password_hash, body.first_name.strip(), body.last_name.strip()),
        )
        conn.commit()
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    finally:
        conn.close()

    set_session_cookie(response, user_row["id"])
    return row_to_user(user_row)


@router.post("/login", response_model=UserOut)
def login(body: LoginRequest, response: Response):
    email = body.email.lower()

    conn = get_connection()
    try:
        user_row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()

    if user_row is None or not verify_password(body.password, user_row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    set_session_cookie(response, user_row["id"])
    return row_to_user(user_row)


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")


def get_optional_current_user(cc_session: str | None = Cookie(default=None)) -> UserOut | None:
    """FastAPI dependency: the logged-in customer, or None for a guest. Never raises."""
    if cc_session is None:
        return None

    user_id = verify_session_token(cc_session)
    if user_id is None:
        return None

    conn = get_connection()
    try:
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()

    if user_row is None:
        return None

    return row_to_user(user_row)


@router.get("/me", response_model=UserOut | None)
def me(user: UserOut | None = Depends(get_optional_current_user)):
    return user
