#!/usr/bin/env python3
"""Minimal Grok Build agent run (default model)."""

from __future__ import annotations

import asyncio

from xg_agent_sdk import XGAgentOptions, TextMessage, query


async def main() -> None:
    options = XGAgentOptions(
        always_approve=True,
        max_turns=3,
    )
    async for message in query(
        prompt="In one short sentence, what is the current working directory name?",
        options=options,
    ):
        if isinstance(message, TextMessage):
            print(message.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
