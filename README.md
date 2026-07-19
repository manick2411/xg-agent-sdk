# xg-agent-sdk

Python SDK for building autonomous coding agents on the [Grok Build](https://github.com/xai-org/grok-build) harness.

Provides a Claude Agent SDK–style API (`query`, options, streaming messages, multi-turn sessions) while Grok Build handles tools, the agent loop, sessions, MCP, and permissions. Models are pluggable: Grok, Claude, OpenAI, Gemini, Ollama, OpenRouter, or any compatible endpoint.

> Unofficial community project. Not affiliated with xAI.

## Requirements

| Requirement | Notes |
|-------------|--------|
| Python 3.10+ | |
| **Grok Build CLI** | Required — the SDK drives the CLI as the agent harness |
| API credentials | e.g. `XAI_API_KEY`, or `grok login` |

### Recommended install (SDK + compatible CLI)

```bash
pip install "xg-agent-sdk[grok]"
xg-agent-install-grok          # downloads a CLI version known to work with this SDK
export XAI_API_KEY=xai-...     # or: grok login
```

This installs the Python package, then fetches the Grok Build binary into
`~/.local/share/xg-agent-sdk/bin/grok` (and links `~/.grok/bin/grok`). The pin
is defined in the SDK so it stays compatible with the streaming-json protocol
we use.

Equivalent:

```bash
pip install xg-agent-sdk
python -m xg_agent_sdk install-cli
```

### Alternative: use an existing Grok Build install

If you already have the [official CLI](https://x.ai/cli):

```bash
curl -fsSL https://x.ai/cli/install.sh | bash
pip install xg-agent-sdk
```

The SDK looks for `grok` on `PATH`, `GROK_CLI_PATH`, `~/.local/share/xg-agent-sdk/bin`,
and `~/.grok/bin`.

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
        elif isinstance(message, ResultMessage):
            print(f"\n[session={message.session_id}]")

asyncio.run(main())
```

```python
from xg_agent_sdk import collect_text, XGAgentOptions

text = await collect_text(
    "Summarize this repository",
    XGAgentOptions(always_approve=True),
)
```

## Features

- **Streaming agent runs** via `query()` over Grok Build headless mode
- **Multi-turn sessions** with `XGSDKClient` and automatic session resume
- **System prompts** — append rules or fully override the system prompt
- **Tool & permission controls** — allowlists, denylists, permission modes, sandbox
- **Multi-provider models** — register Claude, OpenAI, Gemini, Ollama, OpenRouter, and more
- **Project instructions** — respects `AGENTS.md`, `.grok/rules/`, and related files in `cwd`

## Custom instructions

**Append rules** (recommended — keeps the default harness prompt):

```python
XGAgentOptions(
    rules="You are a security reviewer. Never suggest disabling authentication.",
    # append_system_prompt="...",  # alias of rules
    # rules_file="policy.md",
)
```

**Override the system prompt** (replaces the default; `rules` are ignored when set):

```python
XGAgentOptions(system_prompt="You are a concise code auditor.")
# system_prompt_file="prompts/auditor.md"
```

## Multi-turn

```python
from xg_agent_sdk import XGSDKClient, XGAgentOptions, TextMessage

async with XGSDKClient(XGAgentOptions(always_approve=True)) as client:
    async for msg in client.ask("Read the auth module"):
        pass
    async for msg in client.ask("List all callers of that module"):
        if isinstance(msg, TextMessage):
            print(msg.text, end="")
```

## Multi-provider models

Grok Build is the harness; inference is configured per model:

```python
from xg_agent_sdk import (
    register_model,
    anthropic_claude,
    openai_gpt,
    ollama_local,
    collect_text,
    XGAgentOptions,
)

register_model(**anthropic_claude(name="claude", model="claude-sonnet-4"))
register_model(**openai_gpt(name="openai", model="gpt-4o"))
register_model(**ollama_local(name="ollama", model="qwen2.5-coder"))

text = await collect_text(
    "Say hello",
    XGAgentOptions(model="claude", always_approve=True),
)
```

| Provider   | `api_backend`              | Environment variable   |
|------------|----------------------------|------------------------|
| xAI Grok   | built-in / `responses`     | `XAI_API_KEY`          |
| Anthropic  | `messages`                 | `ANTHROPIC_API_KEY`    |
| OpenAI     | `chat_completions` / `responses` | `OPENAI_API_KEY` |
| Gemini     | `chat_completions`         | `GOOGLE_API_KEY`       |
| Ollama     | `chat_completions`         | —                      |
| OpenRouter | `chat_completions`         | `OPENROUTER_API_KEY`   |

See [docs/providers.md](docs/providers.md) for details.

## Configuration reference

| `XGAgentOptions` field   | Grok Build flag                 |
|--------------------------|---------------------------------|
| `model`                  | `-m`                            |
| `cwd`                    | `--cwd`                         |
| `system_prompt`          | `--system-prompt-override`      |
| `rules`                  | `--rules`                       |
| `max_turns`              | `--max-turns`                   |
| `permission_mode`        | `--permission-mode`             |
| `allowed_tools`          | `--tools`                       |
| `disallowed_tools`       | `--disallowed-tools`            |
| `resume`                 | `--resume`                      |
| `continue_session`       | `--continue`                    |
| `always_approve`         | `--always-approve`              |
| `sandbox`                | `--sandbox`                     |
| `agents`                 | `--agents`                      |

Claude-style tool aliases (`Read`, `Bash`, …) map to Grok IDs (`read_file`, `run_terminal_cmd`, …) when `map_tool_aliases=True` (default).

Native tool IDs include: `read_file`, `search_replace`, `run_terminal_cmd`, `grep`, `list_dir`, `web_search`, `web_fetch`, `Agent`.

Full API: [docs/api.md](docs/api.md).

## Examples

```bash
python examples/quick_start_grok.py
python examples/custom_system_prompt.py
python examples/multi_turn_client.py
python examples/read_only_review.py .
python examples/with_claude.py
python examples/with_openai.py
python examples/with_ollama.py
```

## Development

```bash
git clone https://github.com/manick2411/xg-agent-sdk.git
cd xg-agent-sdk
pip install -e ".[dev]"
pytest
```

Optional live tests (requires Grok Build + auth):

```bash
GROK_E2E=1 pytest -m e2e
```

## License

[Apache License 2.0](LICENSE)
