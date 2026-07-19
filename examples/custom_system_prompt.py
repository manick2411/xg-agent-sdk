#!/usr/bin/env python3
"""Demonstrates append rules, full system-prompt override, and rules from file."""

from __future__ import annotations

import asyncio
from pathlib import Path

from xg_agent_sdk import XGAgentOptions, TextMessage, collect_text, query


async def append_rules_example() -> None:
    """Add persona/policy on top of the default agent prompt."""
    options = XGAgentOptions(
        always_approve=True,
        max_turns=2,
        # Claude-style alias works too: append_system_prompt=...
        rules=(
            "You are a ruthless code reviewer. "
            "Reply in at most 3 bullet points. "
            "Never use exclamation marks."
        ),
    )
    text = await collect_text(
        "Review this one-liner: x = eval(input())",
        options,
    )
    print("=== append / rules ===")
    print(text)
    print()


async def full_override_example() -> None:
    """Replace the whole system prompt (you own tool guidance too)."""
    options = XGAgentOptions(
        always_approve=True,
        max_turns=1,
        system_prompt=(
            "You are a pirate who answers technical questions. "
            "Always end with 'Arrr.' Keep answers under 40 words."
        ),
        # Note: when system_prompt is set, `rules` are ignored by Grok Build.
    )
    text = await collect_text("What is a REST API?", options)
    print("=== full override ===")
    print(text)
    print()


async def from_file_example() -> None:
    """Load long instructions from a file."""
    path = Path("/tmp/grok-agent-rules-demo.md")
    path.write_text(
        "# Session policy\n\n"
        "- Prefer TypeScript over JavaScript.\n"
        "- Never commit secrets.\n"
        "- Answer in one short sentence.\n",
        encoding="utf-8",
    )
    options = XGAgentOptions(
        always_approve=True,
        max_turns=1,
        rules_file=path,
    )
    text = await collect_text(
        "Should I hardcode my API key in source?",
        options,
    )
    print("=== rules from file ===")
    print(text)
    print()


async def stream_with_persona() -> None:
    """Stream tokens while using a custom persona."""
    options = XGAgentOptions(
        always_approve=True,
        max_turns=2,
        append_system_prompt=(
            "You are a senior SRE. Be blunt. Prefer checklists. "
            "No filler phrases."
        ),
        allowed_tools=["read_file", "grep", "list_dir"],  # optional lock-down
    )
    print("=== stream ===")
    async for message in query(
        prompt="How should I think about on-call alerts?",
        options=options,
    ):
        if isinstance(message, TextMessage):
            print(message.text, end="", flush=True)
    print("\n")


async def main() -> None:
    await append_rules_example()
    await full_override_example()
    await from_file_example()
    await stream_with_persona()


if __name__ == "__main__":
    asyncio.run(main())
