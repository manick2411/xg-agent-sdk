# xg-agent-sdk

**Programmatic agents with the [Grok Build](https://github.com/xai-org/grok-build) harness — any model.**

A Claude Agent SDK–shaped Python library. You get the same agent loop, tools, sessions, MCP, and permissions that power Grok Build, callable from Python. Inference can use **Grok, Claude, OpenAI, Gemini (OpenAI-compat), Ollama**, or any endpoint Grok Build supports.

> **Not an official xAI product.** This is a thin open wrapper around the open-source Grok Build CLI. Grok Build, Grok, and xAI are trademarks of their owners.

## Why this exists

| Layer | What you get |
|-------|----------------|
| **Claude Agent SDK** | Library on top of Claude Code |
| **xai-sdk** | Chat/API client — *you* implement the tool loop |
| **Grok Build CLI** | Full harness (open source) — headless + ACP, no Python API |
| **xg-agent-sdk** | Library on top of Grok Build (this project) |

There is no published official “XG Agent SDK” package today. Grok Build’s CLI already exposes headless streaming JSON and multi-provider custom models; this SDK makes that ergonomic.

## Install

```bash
# Prerequisites: Grok Build CLI
curl -fsSL https://x.ai/cli/install.sh | bash

# From PyPI (after publish)
pip install xg-agent-sdk

# From source
git clone https://github.com/manick2411/xg-agent-sdk.git
cd xg-agent-sdk
pip install -e ".[dev]"
```

> **Note:** PyPI name is `xg-agent-sdk` (import `xg_agent_sdk`). The name `grok-agent-sdk` was already reserved on PyPI by a third-party placeholder.

Auth (any one):

```bash
export XAI_API_KEY=xai-...   # for default Grok models
# or: grok login
```

## Quick start

```python
import asyncio
from xg_agent_sdk import query, XGAgentOptions, TextMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=XGAgentOptions(
            allowed_tools=["read_file", "search_replace", "run_terminal_cmd"],
            permission_mode="acceptEdits",
            always_approve=True,
            cwd=".",
        ),
    ):
        if isinstance(message, TextMessage):
            print(message.text, end="", flush=True)
        if isinstance(message, ResultMessage):
            print(f"\n[session={message.session_id} cost={message.total_cost_usd}]")

asyncio.run(main())
```

One-shot helper:

```python
from xg_agent_sdk import collect_text, XGAgentOptions

text = await collect_text("Summarize this repo", XGAgentOptions(always_approve=True))
```

## Multi-provider (Claude, OpenAI, Gemini, Ollama, …)

Grok Build is the **harness**; the **model** is pluggable via custom models (`chat_completions`, `responses`, or Anthropic `messages`).

```python
from xg_agent_sdk import (
    register_model,
    anthropic_claude,
    openai_gpt,
    gemini_openai_compat,
    ollama_local,
    openrouter,
    XGAgentOptions,
    collect_text,
)

# Writes [model.*] into ~/.grok/config.toml (creates a .bak backup)
register_model(**anthropic_claude(name="claude", model="claude-sonnet-4"))
register_model(**openai_gpt(name="openai", model="gpt-4o"))
register_model(**gemini_openai_compat(name="gemini", model="gemini-2.5-pro"))
register_model(**ollama_local(name="ollama", model="qwen2.5-coder"))
register_model(**openrouter(name="or", model="anthropic/claude-sonnet-4"))

text = await collect_text(
    "Say hi",
    XGAgentOptions(model="claude", always_approve=True),
)
```

| Provider | Backend | Typical env |
|----------|---------|-------------|
| xAI Grok | built-in / `responses` | `XAI_API_KEY` |
| Anthropic Claude | `messages` | `ANTHROPIC_API_KEY` |
| OpenAI | `chat_completions` or `responses` | `OPENAI_API_KEY` |
| Gemini | OpenAI-compat `chat_completions` | `GOOGLE_API_KEY` |
| Ollama | `chat_completions` local | none |
| OpenRouter | `chat_completions` | `OPENROUTER_API_KEY` |

**Caveat:** Tool-calling quality varies by model. Stronger models work better with multi-step agent tools; small local models may struggle.

## Custom system prompts & instructions

You can shape agent behavior three ways:

### 1. Append rules (recommended)

Keeps Grok Build’s default harness prompt (tools, safety, agent loop) and adds yours:

```python
options = XGAgentOptions(
    always_approve=True,
    rules="You are a strict security reviewer. Never suggest disabling auth.",
    # or Claude-style alias:
    # append_system_prompt="...",
    # rules_file="prompts/policy.md",
)
```

### 2. Full system prompt override

Replaces the entire default system prompt (you own the wording; tool quality may drop if you strip agent guidance):

```python
options = XGAgentOptions(
    system_prompt="You are a pirate engineer. Always end with Arrr.",
    # system_prompt_file="prompts/pirate.md",
)
```

When `system_prompt` is set, Grok **ignores** `rules` / `append_system_prompt` for that run.

### 3. Project files (automatic)

If `cwd` points at a repo with `AGENTS.md`, `.grok/rules/*.md`, or `CLAUDE.md`, Grok Build loads those automatically — no SDK flag required.

```python
XGAgentOptions(cwd="/path/to/project", always_approve=True)
```

See `examples/custom_system_prompt.py`.

## Multi-turn sessions

```python
from xg_agent_sdk import XGSDKClient, XGAgentOptions, TextMessage

async with XGSDKClient(XGAgentOptions(always_approve=True)) as client:
    async for msg in client.ask("Remember codeword: pineapple"):
        ...
    async for msg in client.ask("What was the codeword?"):
        if isinstance(msg, TextMessage):
            print(msg.text, end="")
```

## Architecture

```
Your app  →  xg-agent-sdk  →  grok CLI (subprocess, streaming-json)
                                   │
                                   ├─ tools / sessions / MCP / permissions
                                   └─ HTTP → Grok | Claude | OpenAI | Gemini | Ollama
```

The SDK does **not** reimplement the agent loop. Grok Build remains the brain.

## Options → CLI map

| `XGAgentOptions` | CLI flag |
|--------------------|----------|
| `model` | `-m` |
| `cwd` | `--cwd` |
| `system_prompt` | `--system-prompt-override` |
| `rules` | `--rules` |
| `max_turns` | `--max-turns` |
| `permission_mode` | `--permission-mode` |
| `allowed_tools` | `--tools` |
| `disallowed_tools` | `--disallowed-tools` |
| `resume` | `--resume` |
| `continue_session` | `--continue` |
| `always_approve` | `--always-approve` |
| `sandbox` | `--sandbox` |
| `agents` | `--agents` JSON |

Claude-style tool aliases (`Read`, `Bash`, …) map to Grok IDs (`read_file`, `run_terminal_cmd`, …) when `map_tool_aliases=True` (default).

## Tool IDs (native)

`read_file`, `search_replace`, `run_terminal_cmd`, `grep`, `list_dir`, `web_search`, `web_fetch`, `Agent`, …

## Examples

```bash
python examples/quick_start_grok.py
python examples/read_only_review.py /path/to/repo
python examples/multi_turn_client.py
# optional providers:
python examples/with_claude.py
python examples/with_openai.py
python examples/with_ollama.py
```

## Development

```bash
pip install -e ".[dev]"
pytest                    # unit tests
GROK_E2E=1 pytest -m e2e  # live CLI (optional)
```

## Comparison with Claude Agent SDK

| Concept | Claude Agent SDK | xg-agent-sdk |
|---------|------------------|----------------|
| One-shot | `query()` | `query()` |
| Options | `ClaudeAgentOptions` | `XGAgentOptions` |
| Multi-turn | `ClaudeSDKClient` | `XGSDKClient` |
| Harness | Claude Code CLI | Grok Build CLI |
| Multi-model | limited / platform | first-class custom models |

## License

Apache-2.0. See [LICENSE](LICENSE).
