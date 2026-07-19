from __future__ import annotations

from xg_agent_sdk._argv import build_argv
from xg_agent_sdk.types import XGAgentOptions


def test_basic_argv():
    argv, temp = build_argv("hello", XGAgentOptions(), cli_path="/bin/grok")
    assert temp is None
    assert argv[0] == "/bin/grok"
    assert "-p" in argv
    assert argv[argv.index("-p") + 1] == "hello"
    assert "--output-format" in argv
    assert "streaming-json" in argv
    assert "--no-auto-update" in argv


def test_tools_and_aliases():
    opts = XGAgentOptions(
        allowed_tools=["Read", "Bash"],
        disallowed_tools=["WebSearch"],
        map_tool_aliases=True,
        model="grok-4.5",
        max_turns=3,
        permission_mode="acceptEdits",
        always_approve=True,
        cwd="/tmp/proj",
    )
    argv, _ = build_argv("x", opts, cli_path="grok")
    tools = argv[argv.index("--tools") + 1]
    assert tools == "read_file,run_terminal_cmd"
    denied = argv[argv.index("--disallowed-tools") + 1]
    assert denied == "web_search"
    assert argv[argv.index("-m") + 1] == "grok-4.5"
    assert argv[argv.index("--max-turns") + 1] == "3"
    assert "--always-approve" in argv
    assert argv[argv.index("--cwd") + 1] == "/tmp/proj"


def test_resume_and_agents_json():
    opts = XGAgentOptions(
        resume="abc-123",
        agents={"reviewer": {"prompt": "review"}},
        allow=["Bash(npm*)"],
        deny=["Bash(rm*)"],
    )
    argv, _ = build_argv("x", opts, cli_path="grok")
    assert argv[argv.index("--resume") + 1] == "abc-123"
    assert "--agents" in argv
    assert '"reviewer"' in argv[argv.index("--agents") + 1]
    assert argv.count("--allow") == 1
    assert argv.count("--deny") == 1


def test_long_prompt_uses_file():
    big = "x" * 40_000
    argv, temp = build_argv(big, XGAgentOptions(), cli_path="grok")
    assert temp is not None
    assert "--prompt-file" in argv
    assert temp.read_text(encoding="utf-8") == big
    temp.unlink()


def test_system_prompt_override():
    opts = XGAgentOptions(system_prompt="You are a lint bot.")
    argv, _ = build_argv("x", opts, cli_path="grok")
    assert argv[argv.index("--system-prompt-override") + 1] == "You are a lint bot."
    assert "--rules" not in argv


def test_append_rules_and_alias_merge(tmp_path):
    rules_file = tmp_path / "r.md"
    rules_file.write_text("From file.", encoding="utf-8")
    opts = XGAgentOptions(
        rules="Base rules.",
        append_system_prompt="Extra persona.",
        rules_file=rules_file,
    )
    argv, _ = build_argv("x", opts, cli_path="grok")
    rules_arg = argv[argv.index("--rules") + 1]
    assert "Base rules." in rules_arg
    assert "Extra persona." in rules_arg
    assert "From file." in rules_arg
    assert "--system-prompt-override" not in argv


def test_override_wins_over_rules():
    """Grok ignores --rules when override is set; we only pass override."""
    opts = XGAgentOptions(
        system_prompt="OVERRIDE",
        rules="SHOULD_NOT_APPEAR",
        append_system_prompt="ALSO_NOT",
    )
    argv, _ = build_argv("x", opts, cli_path="grok")
    assert argv[argv.index("--system-prompt-override") + 1] == "OVERRIDE"
    assert "--rules" not in argv
