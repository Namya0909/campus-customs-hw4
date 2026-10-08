"""Pydantic types for the shop chatbot: chat requests/replies, product cards, and audit logging."""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """One prior turn in the conversation, as the frontend already renders it."""

    role: Literal["user", "assistant"]
    content: str


class PageContext(BaseModel):
    """What the shopper is currently looking at in the UI, if anything."""

    product_id: str = Field(description="The product_id of the detail page currently open.")
    product_title: str = Field(description="That product's display name, for a human-readable prompt.")


class ChatRequest(BaseModel):
    """Body of POST /chat."""

    message: str = Field(min_length=1, max_length=2000, description="The customer's new message.")
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior turns in this conversation, oldest first. Does not include `message`.",
    )
    page_context: PageContext | None = Field(
        default=None,
        description="The product detail page the shopper is viewing, if any, so pronouns like "
        "'this'/'it' can be resolved to a specific product.",
    )


class SizeAvailability(BaseModel):
    """One size's exact stock count, read directly from the inventory table."""

    size: str
    quantity: int = Field(description="Exact units in stock for this size, straight from inventory.quantity.")
    available: bool = Field(description="quantity > 0 — lets the agent state availability without doing math.")


class ProductCard(BaseModel):
    """Lightweight product payload the frontend renders as a card under a chat reply."""

    product_id: str
    name: str
    price: float
    image_url: str
    garment_type: str
    in_stock: bool = Field(description="True if at least one size currently has stock.")


class ProductDetail(ProductCard):
    """Full detail for one product, returned by the get_product_details tool."""

    description: str
    colors: list[str]
    sizes: list[SizeAvailability]


class StockLookup(BaseModel):
    """Structured result of a stock check, read directly from the inventory table.

    Always carries the full per-size breakdown (not just the requested size) so the agent
    can point the shopper to an in-stock alternative when the size they asked about is out.
    """

    product_id: str
    found: bool = Field(description="False if no catalogue product has this product_id.")
    requested_size: str | None = Field(default=None, description="The specific size the shopper asked about, if any.")
    requested_size_available: bool | None = Field(
        default=None,
        description=(
            "Whether requested_size specifically is in stock. Null if no specific size was "
            "requested, or if the product wasn't found."
        ),
    )
    sizes: list[SizeAvailability] = Field(
        default_factory=list, description="Every size this product comes in, each with its exact quantity."
    )


class ChatReply(BaseModel):
    """Structured output the agent must produce for every turn."""

    message: str = Field(description="The conversational reply to show in the chat panel.")
    products: list[ProductCard] = Field(
        default_factory=list,
        description="Catalogue products relevant to this reply, grounded in a tool call this turn. Empty if none.",
    )


class ChatHistoryEntry(BaseModel):
    """One saved turn, as returned by GET /api/chat/history to repopulate the widget on login."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(
        default_factory=list, description="Product cards attached to this turn, if it was an assistant reply."
    )


# --- Audit logging (output/audit_trail.json) ---


class ToolCallRecord(BaseModel):
    """One tool call made during a turn, with its arguments and result shortened for the log."""

    tool_name: str
    tool_args: dict = Field(default_factory=dict, description="This call's arguments, values truncated for the log.")
    tool_result_summary: str = Field(description="Short, human-readable summary of what the tool returned.")


class AuditEntry(BaseModel):
    """One structured log record for one /chat turn, appended to output/audit_trail.json."""

    timestamp: str = Field(description="ISO-8601 UTC timestamp for when the turn finished.")
    user_message: str = Field(description="The shopper's message this turn, truncated.")
    tool_calls: list[ToolCallRecord] = Field(default_factory=list, description="Every tool call made this turn, in order.")
    stop_reason: str = Field(description="How the turn ended, e.g. 'completed' or 'error: <ExceptionType>'.")
    output_summary: str = Field(description="Shortened assistant reply text, or empty on error.")
