"""Campus Customs shop chatbot agent (PydanticAI + gpt-5.6-luna via Portkey).

Loads the system prompt from prompts/prompt.md and the model/API key from a
.env file (PORTKEY_API_KEY, optionally MODEL_NAME / PORTKEY_BASE_URL) — same
convention as the other homeworks' agents.
"""

import os
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, ToolReturnPart, UserPromptPart
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from audit import append_audit, build_audit_entry
from db import get_connection
from models import ChatMessage, ChatReply, PageContext
from tools import check_stock, get_product_details, product_card_from_row, search_products

# The three tools that are allowed to back a claim in `ChatReply.products` or in any
# price/description/stock statement in `ChatReply.message`.
LOOKUP_TOOLS = {"search_products", "get_product_details", "check_stock"}


def _lookup_tool_was_called(messages: list[ModelMessage]) -> bool:
    return any(
        isinstance(part, ToolReturnPart) and part.tool_name in LOOKUP_TOOLS
        for message in messages
        for part in getattr(message, "parts", [])
    )


@dataclass
class ChatDeps:
    """Per-request context the agent can read but the model never has to be told verbatim.

    Injected once per run via `Agent.run(..., deps=...)` and read back inside a dynamic
    system prompt function — this is how customer identity and page context reach the agent
    without being smuggled into the conversation as fake user/assistant messages.
    """

    customer_name: str | None  # None for a guest shopper
    customer_email: str | None
    page_context: PageContext | None  # the product detail page currently open, if any


BACKEND_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"

# The .env may sit in this folder or any parent (e.g. the repo root).
for folder in (BACKEND_DIR, *BACKEND_DIR.parents):
    load_dotenv(folder / ".env", override=False)

MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.6-luna")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")


def make_client() -> AsyncOpenAI:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set (put it in a .env file in this folder or a parent).")
    return AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
    )


def build_message_history(history: list[ChatMessage]) -> list[ModelRequest | ModelResponse]:
    """Turn the frontend's plain role/content history into PydanticAI message objects."""
    messages: list[ModelRequest | ModelResponse] = []
    for turn in history:
        if turn.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return messages


def build_agent() -> Agent[ChatDeps, ChatReply]:
    client = make_client()
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=ChatReply,
        system_prompt=PROMPT_PATH.read_text(encoding="utf-8"),
        tools=[search_products, get_product_details, check_stock],
        retries=2,
    )

    @agent.system_prompt
    def customer_and_page_context(ctx: RunContext[ChatDeps]) -> str:
        """Appended to prompt.md's static persona on every run — never hard-coded in the file."""
        deps = ctx.deps
        lines = ["## This conversation's context"]

        if deps.customer_name:
            lines.append(
                f"- Logged-in customer: {deps.customer_name} ({deps.customer_email}). You may use their "
                "first name naturally (e.g. a greeting), but don't overdo it or use it in every reply."
            )
        else:
            lines.append("- Guest shopper: not logged in. Don't address them by name or guess who they are.")

        if deps.page_context:
            lines.append(
                f"- They are currently viewing the product page for '{deps.page_context.product_title}' "
                f"(product_id={deps.page_context.product_id}). If they use a pronoun like 'this' or 'it' "
                "without naming a product, assume they mean this one — but still call get_product_details "
                "or check_stock on it before answering; the page being open is a hint about *which* "
                "product they mean, not a substitute for looking up its actual price/description/stock."
            )
        else:
            lines.append("- They are not currently viewing any specific product page.")

        return "\n".join(lines)

    @agent.output_validator
    def ground_products(ctx: RunContext[ChatDeps], result: ChatReply) -> ChatReply:
        """Reject any reply that names products without having actually looked them up this turn."""
        if not result.products:
            return result

        if not _lookup_tool_was_called(ctx.messages):
            raise ModelRetry(
                "You listed products in `products` without calling search_products, "
                "get_product_details, or check_stock this turn. Call one of those tools first — "
                "never state a product's name, price, description, or stock from memory, even if "
                "it was already discussed earlier in this conversation."
            )

        # Re-fetch every product_id from the DB so the reply can't carry stale or hallucinated
        # field values even when the tool really was called.
        conn = get_connection()
        try:
            grounded = []
            for card in result.products:
                row = conn.execute(
                    "SELECT * FROM catalogue WHERE product_id = ?", (card.product_id,)
                ).fetchone()
                if row is not None:
                    grounded.append(product_card_from_row(conn, row))
        finally:
            conn.close()

        if not grounded:
            raise ModelRetry(
                "None of the product_ids in `products` exist in the catalogue. Call search_products "
                "or get_product_details first, and only use the product_ids those tools returned."
            )
        result.products = grounded
        return result

    return agent


_agent: Agent[ChatDeps, ChatReply] | None = None


def get_agent() -> Agent[ChatDeps, ChatReply]:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


async def run_chat(
    message: str,
    history: list[ChatMessage],
    *,
    customer_name: str | None = None,
    customer_email: str | None = None,
    page_context: PageContext | None = None,
) -> ChatReply:
    agent = get_agent()
    deps = ChatDeps(customer_name=customer_name, customer_email=customer_email, page_context=page_context)

    try:
        run = await agent.run(message, deps=deps, message_history=build_message_history(history))
    except Exception as exc:
        append_audit([build_audit_entry(message, [], f"error: {type(exc).__name__}", "")])
        raise

    reply = run.output
    append_audit([build_audit_entry(message, run.all_messages(), "completed", reply.message)])
    return reply
