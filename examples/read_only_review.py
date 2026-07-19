#!/usr/bin/env python3
"""Read-only code review agent (no shell, no edits)."""

from __future__ import annotations

import asyncio
import sys

from xg_agent_sdk import XGAgentOptions, TextMessage, query


async def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    options = XGAgentOptions(
        always_approve=True,
        allowed_tools=["read_file", "grep", "list_dir"],
        disallowed_tools=["run_terminal_cmd", "search_replace", "web_search", "web_fetch"],
        max_turns=12,
        cwd=target,
    )
    prompt = (
        f"Review the codebase at {target} for obvious bugs and security issues. "
        "Be concise. Do not modify files."
    )
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, TextMessage):
            print(message.text, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
