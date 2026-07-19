"""Parse Grok Build streaming-json NDJSON lines into Message objects."""

from __future__ import annotations

import json
from typing import Any

from .errors import CLIJSONDecodeError
from .types import (
    ErrorMessage,
    Message,
    ResultMessage,
    SystemMessage,
    TextMessage,
    ThoughtMessage,
)


def parse_line(line: str) -> Message | None:
    """Parse one NDJSON line. Returns None for blank lines."""
    stripped = line.strip()
    if not stripped:
        return None
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise CLIJSONDecodeError(
            f"Failed to parse streaming-json line: {exc}", line=stripped
        ) from exc
    if not isinstance(data, dict):
        raise CLIJSONDecodeError(
            f"Expected JSON object, got {type(data).__name__}", line=stripped
        )
    return event_to_message(data)


def event_to_message(data: dict[str, Any]) -> Message:
    """Convert a parsed event dict to a Message."""
    event_type = data.get("type")

    if event_type == "text":
        return TextMessage(text=str(data.get("data", "")), raw=data)

    if event_type == "thought":
        return ThoughtMessage(text=str(data.get("data", "")), raw=data)

    if event_type == "end":
        # Prefer explicit text if present; callers usually pass accumulated text
        text = data.get("text")
        return ResultMessage(
            result=str(text) if text is not None else "",
            stop_reason=data.get("stopReason") or data.get("stop_reason"),
            session_id=data.get("sessionId") or data.get("session_id"),
            request_id=data.get("requestId") or data.get("request_id"),
            usage=data.get("usage"),
            num_turns=data.get("num_turns") or data.get("numTurns"),
            total_cost_usd=data.get("total_cost_usd") or data.get("totalCostUsd"),
            model_usage=data.get("modelUsage") or data.get("model_usage"),
            raw=data,
        )

    if event_type == "error":
        msg = data.get("message") or data.get("data") or "Unknown Grok Build error"
        return ErrorMessage(message=str(msg), raw=data)

    # Forward-compatible: max_turns_reached, auto_compact_*, etc.
    subtype = str(event_type) if event_type is not None else "unknown"
    return SystemMessage(subtype=subtype, data=data, raw=data)


class StreamAccumulator:
    """Accumulate text chunks and attach full text to ResultMessage on end."""

    def __init__(self) -> None:
        self.text_parts: list[str] = []
        self.session_id: str | None = None

    def process(self, message: Message) -> Message:
        if isinstance(message, TextMessage):
            self.text_parts.append(message.text)
            return message
        if isinstance(message, ResultMessage):
            full = "".join(self.text_parts)
            if not message.result:
                message.result = full
            if message.session_id:
                self.session_id = message.session_id
            return message
        if isinstance(message, ErrorMessage):
            return message
        return message
