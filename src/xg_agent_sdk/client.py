"""Multi-turn ``XGSDKClient`` with session resume."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import replace

from ._transport.subprocess import run_streaming_query
from .types import XGAgentOptions, Message, ResultMessage


class XGSDKClient:
    """Stateful multi-turn client over headless Grok Build sessions.

    Each ``query()`` spawns a new ``grok`` process. After the first result,
    subsequent prompts pass ``--resume <session_id>`` so context accumulates.
    """

    def __init__(self, options: XGAgentOptions | None = None) -> None:
        self._base_options = options or XGAgentOptions()
        self._session_id: str | None = self._base_options.resume
        self._pending_prompt: str | None = None
        self._closed = False

    @property
    def session_id(self) -> str | None:
        return self._session_id

    async def __aenter__(self) -> XGSDKClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()

    async def close(self) -> None:
        self._closed = True
        self._pending_prompt = None

    async def query(self, prompt: str) -> None:
        """Queue a user prompt. Consume with :meth:`receive_response`."""
        if self._closed:
            raise RuntimeError("XGSDKClient is closed")
        self._pending_prompt = prompt

    async def receive_response(self) -> AsyncIterator[Message]:
        """Stream messages for the last queued prompt."""
        if self._pending_prompt is None:
            raise RuntimeError("No pending prompt; call query() first")
        prompt = self._pending_prompt
        self._pending_prompt = None

        opts = replace(self._base_options)
        if self._session_id:
            opts.resume = self._session_id
            opts.continue_session = False

        async for message in run_streaming_query(prompt, opts):
            if isinstance(message, ResultMessage) and message.session_id:
                self._session_id = message.session_id
            yield message

    async def ask(self, prompt: str) -> AsyncIterator[Message]:
        """Convenience: query + stream response in one call."""
        await self.query(prompt)
        async for message in self.receive_response():
            yield message
