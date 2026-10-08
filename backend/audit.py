"""Append-only audit log for the shop agent, written to output/audit_trail.json.

One AuditEntry per /chat turn: a timestamp, every tool call made that turn (name, shortened
args, shortened result), how the turn ended (stop_reason), and a shortened copy of the final
reply. Nothing is ever removed or rewritten — append_audit() only ever adds entries, and every
prior entry survives restarts because it's read back from disk, not kept in memory.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai._output import DEFAULT_OUTPUT_TOOL_NAME
from pydantic_ai.messages import ModelMessage, ToolCallPart, ToolReturnPart

from models import AuditEntry, ToolCallRecord

BACKEND_DIR = Path(__file__).resolve().parent
AUDIT_PATH = BACKEND_DIR.parent / "output" / "audit_trail.json"

MAX_FIELD_LENGTH = 200


def _shorten(value: object) -> object:
    """Truncate a single value (string, or any other value via str()) for the log."""
    text = value if isinstance(value, str) else str(value)
    return text if len(text) <= MAX_FIELD_LENGTH else text[: MAX_FIELD_LENGTH - 1] + "…"


def _shorten_args(args: dict) -> dict:
    return {key: _shorten(value) for key, value in args.items()}


def _summarize_tool_result(content: object) -> str:
    """Short, human-readable summary of what a tool returned — never the raw object."""
    if isinstance(content, list):
        names = [getattr(item, "name", str(item)) for item in content]
        return _shorten(f"{len(content)} product(s): {', '.join(names)}" if names else "0 products")
    if hasattr(content, "found") and hasattr(content, "sizes"):
        # StockLookup
        if not content.found:
            return "product not found"
        sizes = ", ".join(f"{s.size}={s.quantity}" for s in content.sizes)
        return _shorten(f"found; requested_size_available={content.requested_size_available}; sizes: {sizes}")
    if content is None:
        return "not found"
    if hasattr(content, "name"):
        # ProductDetail
        return _shorten(f"{content.name} (${content.price})")
    return _shorten(content)


def build_audit_entry(user_message: str, messages: list[ModelMessage], stop_reason: str, output_summary: str) -> AuditEntry:
    """Walk one run's messages into one AuditEntry: every real tool call, in order."""
    returns_by_id: dict[str, object] = {}
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolReturnPart):
                returns_by_id[part.tool_call_id] = part.content

    tool_calls: list[ToolCallRecord] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart) and part.tool_name != DEFAULT_OUTPUT_TOOL_NAME:
                args = part.args_as_dict() if hasattr(part, "args_as_dict") else part.args
                if not isinstance(args, dict):
                    args = {"raw_args": str(args)}
                tool_calls.append(
                    ToolCallRecord(
                        tool_name=part.tool_name,
                        tool_args=_shorten_args(args),
                        tool_result_summary=_summarize_tool_result(returns_by_id.get(part.tool_call_id)),
                    )
                )

    return AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(),
        user_message=_shorten(user_message),
        tool_calls=tool_calls,
        stop_reason=stop_reason,
        output_summary=_shorten(output_summary),
    )


def append_audit(entries: list[AuditEntry]) -> None:
    """Add entries to output/audit_trail.json without touching any entry already there.

    Implemented as read-existing-array, append, write-whole-array-back, since a JSON file
    can't be appended to byte-by-byte and stay valid — but no prior entry is ever read back
    only to be dropped, edited, or reordered, so the log itself is still strictly append-only.
    """
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if AUDIT_PATH.exists():
        try:
            existing = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            existing = []

    existing.extend(entry.model_dump() for entry in entries)
    AUDIT_PATH.write_text(json.dumps(existing, indent=2), encoding="utf-8")
