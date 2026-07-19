#!/usr/bin/env python3
"""Use Grok Build harness with Anthropic Claude as the model.

Requires:
  - grok CLI installed
  - ANTHROPIC_API_KEY set
  - Network access to api.anthropic.com
"""

from __future__ import annotations

import asyncio
import os

from xg_agent_sdk import (
    XGAgentOptions,
    anthropic_claude,
    collect_text,
    register_model,
)


async def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit("Set ANTHROPIC_API_KEY first")

    # Writes [model.claude] into ~/.grok/config.toml (with backup)
    register_model(**anthropic_claude(name="claude", model="claude-sonnet-4"))

    text = await collect_text(
        "Say hello in exactly five words.",
        XGAgentOptions(model="claude", always_approve=True, max_turns=2),
    )
    print(text)


if __name__ == "__main__":
    asyncio.run(main())
