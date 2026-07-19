#!/usr/bin/env python3
"""Multi-turn conversation with session resume."""

from __future__ import annotations

import asyncio

from xg_agent_sdk import XGAgentOptions, XGSDKClient, ResultMessage, TextMessage


async def main() -> None:
    options = XGAgentOptions(always_approve=True, max_turns=4)
    async with XGSDKClient(options) as client:
        async for msg in client.ask("Remember the secret codeword: pineapple. Just acknowledge."):
            if isinstance(msg, TextMessage):
                print(msg.text, end="", flush=True)
            if isinstance(msg, ResultMessage):
                print(f"\n[session={msg.session_id}]")

        print("---")
        async for msg in client.ask("What was the secret codeword?"):
            if isinstance(msg, TextMessage):
                print(msg.text, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
