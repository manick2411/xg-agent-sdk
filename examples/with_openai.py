#!/usr/bin/env python3
"""Grok Build harness + OpenAI model."""

from __future__ import annotations

import asyncio
import os

from xg_agent_sdk import XGAgentOptions, collect_text, openai_gpt, register_model


async def main() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY first")

    register_model(**openai_gpt(name="openai", model="gpt-4o"))
    text = await collect_text(
        "Say hello in exactly five words.",
        XGAgentOptions(model="openai", always_approve=True, max_turns=2),
    )
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
