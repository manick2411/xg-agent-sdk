from __future__ import annotations

import os

import pytest

from xg_agent_sdk import XGAgentOptions, collect_text
from xg_agent_sdk.errors import CLINotFoundError

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
@pytest.mark.skipif(os.environ.get("GROK_E2E") != "1", reason="Set GROK_E2E=1 for live tests")
async def test_live_say_hi():
    try:
        text = await collect_text(
            "Reply with exactly: pong",
            XGAgentOptions(always_approve=True, max_turns=1),
        )
    except CLINotFoundError:
        pytest.skip("grok CLI not installed")
    assert text
    assert "pong" in text.lower() or len(text) > 0
