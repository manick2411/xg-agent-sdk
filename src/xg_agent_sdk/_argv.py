"""Map XGAgentOptions + prompt → CLI argv."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from .types import XGAgentOptions, normalize_tool_name

# Prompt length above which we switch to --prompt-file to avoid OS arg limits
_PROMPT_FILE_THRESHOLD = 32_000


def _tools_csv(tools: list[str], *, map_aliases: bool) -> str:
    names = [normalize_tool_name(t) if map_aliases else t for t in tools]
    return ",".join(names)


def build_argv(
    prompt: str,
    options: XGAgentOptions,
    *,
    cli_path: str,
) -> tuple[list[str], Path | None]:
    """Build argv for a headless agent run.

    Returns ``(argv, temp_prompt_file)``. Caller must delete the temp file if set.
    """
    argv: list[str] = [cli_path]
    temp_prompt: Path | None = None

    if len(prompt) > _PROMPT_FILE_THRESHOLD:
        fd, name = tempfile.mkstemp(prefix="grok-agent-prompt-", suffix=".txt")
        temp_prompt = Path(name)
        with open(fd, "w", encoding="utf-8") as f:
            f.write(prompt)
        argv.extend(["--prompt-file", str(temp_prompt)])
    else:
        argv.extend(["-p", prompt])

    argv.extend(["--output-format", "streaming-json"])

    if options.no_auto_update:
        argv.append("--no-auto-update")

    if options.model:
        argv.extend(["-m", options.model])
    if options.cwd is not None:
        argv.extend(["--cwd", str(Path(options.cwd).expanduser())])

    # System prompt: override replaces defaults; rules only apply without override.
    system_prompt = options.resolved_system_prompt()
    rules = options.resolved_rules()
    if system_prompt:
        # Long prompts: still pass as argv; OS limits are rare for system prompts.
        # If both override + rules were set, Grok ignores rules — prefer override only.
        argv.extend(["--system-prompt-override", system_prompt])
    elif rules:
        argv.extend(["--rules", rules])
    if options.max_turns is not None:
        argv.extend(["--max-turns", str(options.max_turns)])
    if options.permission_mode:
        argv.extend(["--permission-mode", options.permission_mode])
    if options.allowed_tools:
        argv.extend(
            [
                "--tools",
                _tools_csv(options.allowed_tools, map_aliases=options.map_tool_aliases),
            ]
        )
    if options.disallowed_tools:
        argv.extend(
            [
                "--disallowed-tools",
                _tools_csv(
                    options.disallowed_tools, map_aliases=options.map_tool_aliases
                ),
            ]
        )
    if options.resume:
        argv.extend(["--resume", options.resume])
    if options.continue_session:
        argv.append("--continue")
    if options.session_id:
        argv.extend(["--session-id", options.session_id])
    if options.fork_session:
        argv.append("--fork-session")
    if options.always_approve:
        argv.append("--always-approve")
    if options.sandbox:
        argv.extend(["--sandbox", options.sandbox])
    if options.no_subagents:
        argv.append("--no-subagents")
    if options.disable_web_search:
        argv.append("--disable-web-search")
    if options.reasoning_effort:
        argv.extend(["--reasoning-effort", options.reasoning_effort])
    if options.agent:
        argv.extend(["--agent", options.agent])
    if options.agents is not None:
        if isinstance(options.agents, str):
            agents_json = options.agents
        else:
            agents_json = json.dumps(options.agents, separators=(",", ":"))
        argv.extend(["--agents", agents_json])
    if options.allow:
        for rule in options.allow:
            argv.extend(["--allow", rule])
    if options.deny:
        for rule in options.deny:
            argv.extend(["--deny", rule])
    if options.json_schema is not None:
        if isinstance(options.json_schema, str):
            schema = options.json_schema
        else:
            schema = json.dumps(options.json_schema, separators=(",", ":"))
        argv.extend(["--json-schema", schema])
    if options.extra_args:
        argv.extend(options.extra_args)

    return argv, temp_prompt
