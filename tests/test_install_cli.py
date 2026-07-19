from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest

from xg_agent_sdk.install_cli import (
    PINNED_CLI_VERSION,
    _is_semver,
    parse_version,
    version_at_least,
)
from xg_agent_sdk._cli import try_resolve_cli_path
from xg_agent_sdk.errors import CLINotFoundError
from xg_agent_sdk._cli import resolve_cli_path


def test_semver_helpers():
    assert _is_semver("0.2.103")
    assert not _is_semver("latest")
    assert parse_version("0.2.103") == (0, 2, 103)
    assert version_at_least("0.2.103", "0.2.100")
    assert not version_at_least("0.1.0", "0.2.100")


def test_resolve_prefers_explicit(tmp_path: Path):
    fake = tmp_path / "grok"
    fake.write_text("#!/bin/sh\n", encoding="utf-8")
    fake.chmod(0o755)
    assert resolve_cli_path(fake) == str(fake.resolve())


def test_resolve_missing_message():
    with mock.patch("xg_agent_sdk._cli.shutil.which", return_value=None), mock.patch(
        "xg_agent_sdk._cli._SDK_BIN"
    ) as bin_mock, mock.patch("xg_agent_sdk._cli._CANDIDATE_PATHS", ()):
        bin_mock.is_file.return_value = False
        with pytest.raises(CLINotFoundError) as ei:
            resolve_cli_path()
        msg = str(ei.value)
        assert "xg-agent-install-grok" in msg
        assert "xg-agent-sdk[grok]" in msg


def test_try_resolve_none_when_missing():
    with mock.patch("xg_agent_sdk._cli.resolve_cli_path", side_effect=CLINotFoundError("x")):
        assert try_resolve_cli_path() is None


def test_pinned_version_format():
    assert _is_semver(PINNED_CLI_VERSION)
