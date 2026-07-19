# Multi-provider guide

Grok Build speaks three inference protocols. This SDK registers models into
`~/.grok/config.toml` and selects them with `XGAgentOptions(model=...)`.

## Backends

| `api_backend` | Protocol | Use for |
|---------------|----------|---------|
| `chat_completions` | OpenAI Chat Completions | OpenAI, Gemini OpenAI-compat, Ollama, OpenRouter, vLLM, LiteLLM |
| `responses` | OpenAI Responses API | OpenAI Responses-capable endpoints, some xAI paths |
| `messages` | Anthropic Messages | Claude direct |

## Registering models

```python
from xg_agent_sdk import register_model, anthropic_claude

register_model(
    **anthropic_claude(name="claude", model="claude-sonnet-4"),
    config_path=None,  # default ~/.grok/config.toml
    backup=True,
)
```

For tests or isolated configs, pass `config_path=Path("/tmp/demo-config.toml")`.

## Quality notes

- Prefer models with strong tool-calling for multi-step coding agents.
- Ollama / small models: keep `max_turns` low and tool sets small.
- Compaction and some server-side tools (e.g. backend web search) may only
  apply fully on xAI-hosted models.

## Security

- Prefer `env_key` over embedding `api_key` in config.toml.
- `register_model` creates a timestamped `.bak` next to the config file.
- Never commit config files that contain secrets.
