"""Public option and message types."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

PermissionMode = Literal[
    "default",
    "acceptEdits",
    "auto",
    "dontAsk",
    "bypassPermissions",
    "plan",
]

# Optional Claude-style aliases → Grok Build internal tool IDs
TOOL_ALIASES: dict[str, str] = {
    "Read": "read_file",
    "Write": "search_replace",
    "Edit": "search_replace",
    "Bash": "run_terminal_cmd",
    "Shell": "run_terminal_cmd",
    "Glob": "list_dir",
    "Grep": "grep",
    "WebSearch": "web_search",
    "WebFetch": "web_fetch",
    "Agent": "Agent",
}


def normalize_tool_name(name: str) -> str:
    """Map Claude-style aliases to Grok tool IDs; pass through unknown names."""
    return TOOL_ALIASES.get(name, name)


@dataclass
class XGAgentOptions:
    """Configuration for a Grok Build agent run.

    Most fields map 1:1 to ``grok -p`` CLI flags. See README for the full table.

    System prompt customization (pick one strategy):

    * **``system_prompt``** — *replace* the entire default system prompt
      (``--system-prompt-override``). Project ``AGENTS.md`` / rules files still
      load via cwd unless you isolate the working directory.
    * **``rules`` / ``append_system_prompt``** — *append* instructions to the
      default harness prompt (``--rules``). Preferred when you want Grok Build
      tool behavior intact plus your persona/policy.
    * **``system_prompt_file`` / ``rules_file``** — load the text from a path
      (handy for long prompts).

    Note: when ``system_prompt`` is set, Grok Build uses it verbatim and
    **ignores** ``--rules`` / append text for that run.
    """

    model: str | None = None
    cwd: str | Path | None = None
    # --- system prompt / instructions ---
    system_prompt: str | None = None
    """Full system prompt override (replaces default)."""
    system_prompt_file: str | Path | None = None
    """Load ``system_prompt`` from this file if ``system_prompt`` is unset."""
    rules: str | None = None
    """Extra rules appended to the default system prompt (``--rules``)."""
    append_system_prompt: str | None = None
    """Alias of ``rules`` (Claude Agent SDK naming). Merged if both set."""
    rules_file: str | Path | None = None
    """Load append-rules from this file (combined with ``rules`` / append)."""
    # --- agent loop ---
    max_turns: int | None = None
    permission_mode: PermissionMode | str | None = None
    allowed_tools: list[str] | None = None
    disallowed_tools: list[str] | None = None
    map_tool_aliases: bool = True
    resume: str | None = None
    continue_session: bool = False
    session_id: str | None = None
    fork_session: bool = False
    always_approve: bool = False
    sandbox: str | None = None
    no_subagents: bool = False
    disable_web_search: bool = False
    reasoning_effort: str | None = None
    agents: dict[str, Any] | str | None = None
    agent: str | None = None
    allow: list[str] | None = None
    deny: list[str] | None = None
    json_schema: dict[str, Any] | str | None = None
    # Process
    cli_path: str | Path | None = None
    env: dict[str, str] | None = None
    extra_args: list[str] | None = None
    no_auto_update: bool = True
    # When True, raise ProcessError on non-zero exit after streaming
    raise_on_error: bool = True
    # Download a compatible Grok Build CLI if none is found
    auto_install_cli: bool = False

    def resolved_system_prompt(self) -> str | None:
        """Return override text from ``system_prompt`` or ``system_prompt_file``."""
        if self.system_prompt is not None:
            return self.system_prompt
        if self.system_prompt_file is not None:
            return Path(self.system_prompt_file).expanduser().read_text(encoding="utf-8")
        return None

    def resolved_rules(self) -> str | None:
        """Merge ``rules``, ``append_system_prompt``, and ``rules_file``."""
        parts: list[str] = []
        if self.rules:
            parts.append(self.rules)
        if self.append_system_prompt:
            parts.append(self.append_system_prompt)
        if self.rules_file is not None:
            parts.append(
                Path(self.rules_file).expanduser().read_text(encoding="utf-8")
            )
        if not parts:
            return None
        return "\n\n".join(parts)


@dataclass
class TextMessage:
    type: Literal["text"] = "text"
    text: str = ""
    raw: dict[str, Any] | None = None


@dataclass
class ThoughtMessage:
    type: Literal["thought"] = "thought"
    text: str = ""
    raw: dict[str, Any] | None = None


@dataclass
class ResultMessage:
    type: Literal["result"] = "result"
    result: str = ""
    stop_reason: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    usage: dict[str, Any] | None = None
    num_turns: int | None = None
    total_cost_usd: float | None = None
    model_usage: dict[str, Any] | None = None
    raw: dict[str, Any] | None = None


@dataclass
class ErrorMessage:
    type: Literal["error"] = "error"
    message: str = ""
    raw: dict[str, Any] | None = None


@dataclass
class SystemMessage:
    """Forward-compatible wrapper for unknown or lifecycle streaming events."""

    type: Literal["system"] = "system"
    subtype: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] | None = None


Message = TextMessage | ThoughtMessage | ResultMessage | ErrorMessage | SystemMessage
