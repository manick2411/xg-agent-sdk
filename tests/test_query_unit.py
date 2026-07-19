from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from xg_agent_sdk import XGAgentOptions, ResultMessage, TextMessage, query
from xg_agent_sdk.errors import ProcessError


@pytest.mark.asyncio
async def test_query_mocked_subprocess(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    script = tmp_path / "fake_grok.py"
    script.write_text(
        """#!/usr/bin/env python3
import sys
print('{"type":"text","data":"Hello"}')
print('{"type":"text","data":" world"}')
print('{"type":"end","stopReason":"EndTurn","sessionId":"sess-1","num_turns":1}')
sys.exit(0)
""",
        encoding="utf-8",
    )
    script.chmod(0o755)

    opts = XGAgentOptions(cli_path=script, always_approve=True)
    # fake binary is python script — invoke via python by replacing resolve
    # Our resolve needs executable; shebang works if python3 available.

    messages = []
    async for m in query(prompt="hi", options=opts):
        messages.append(m)

    texts = [m for m in messages if isinstance(m, TextMessage)]
    results = [m for m in messages if isinstance(m, ResultMessage)]
    assert "".join(t.text for t in texts) == "Hello world"
    assert len(results) == 1
    assert results[0].result == "Hello world"
    assert results[0].session_id == "sess-1"


@pytest.mark.asyncio
async def test_query_nonzero_exit(tmp_path: Path):
    script = tmp_path / "fail_grok.py"
    script.write_text(
        """#!/usr/bin/env python3
import sys
print('{"type":"error","message":"nope"}')
sys.exit(2)
""",
        encoding="utf-8",
    )
    script.chmod(0o755)

    opts = XGAgentOptions(cli_path=script, raise_on_error=True)
    with pytest.raises(ProcessError) as ei:
        async for _ in query(prompt="x", options=opts):
            pass
    assert ei.value.exit_code == 2
