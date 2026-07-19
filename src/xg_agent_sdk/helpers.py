"""Convenience helpers for common SDK patterns."""

from __future__ import annotations

from .query import query
from .types import ErrorMessage, XGAgentOptions, ResultMessage


async def collect_result(
    prompt: str,
    options: XGAgentOptions | None = None,
) -> ResultMessage:
    """Run a query and return the final :class:`ResultMessage`.

    Raises:
        RuntimeError: if the stream ends without a result.
        ProcessError: if the CLI process fails (when ``raise_on_error``).
    """
    last: ResultMessage | None = None
    err: ErrorMessage | None = None
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            last = message
        elif isinstance(message, ErrorMessage):
            err = message
    if last is not None:
        return last
    if err is not None:
        raise RuntimeError(f"Agent error: {err.message}")
    raise RuntimeError("Agent stream ended without a result message")


async def collect_text(
    prompt: str,
    options: XGAgentOptions | None = None,
) -> str:
    """Run a query and return the final assistant text."""
    result = await collect_result(prompt, options)
    return result.result
