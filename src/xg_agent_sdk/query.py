"""One-shot ``query()`` entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator

from ._transport.subprocess import run_streaming_query
from .types import XGAgentOptions, Message


async def query(
    *,
    prompt: str,
    options: XGAgentOptions | None = None,
) -> AsyncIterator[Message]:
    """Run a single Grok Build agent turn and stream messages.

    This is the Claude Agent SDK–style one-shot API: spawn the harness,
    stream tool/agent progress as NDJSON events, yield typed messages, exit.

    Example::

        async for message in query(prompt="What files are here?"):
            if getattr(message, "type", None) == "text":
                print(message.text, end="", flush=True)
            if getattr(message, "type", None) == "result":
                print()  # done
    """
    async for message in run_streaming_query(prompt, options):
        yield message
