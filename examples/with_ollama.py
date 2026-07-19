#!/usr/bin/env python3
"""Grok Build harness with a local Ollama model."""

from __future__ import annotations

import asyncio

from xg_agent_sdk import XGAgentOptions, collect_text, ollama_local, register_model


async def main() -> None:
    register_model(**ollama_local(name="ollama", model="qwen2.5-coder"))
    text = await collect_text(
        "Say hello in exactly five words.",
        XGAgentOptions(model="ollama", always_approve=True, max_turns=2),
    )
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
