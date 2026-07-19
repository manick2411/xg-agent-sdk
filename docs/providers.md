# Multi-provider models

Grok Build supports three inference backends. This SDK registers models in Grok’s config (`~/.grok/config.toml` by default) and selects them with `XGAgentOptions(model=...)`.

## Backends

| `api_backend` | Protocol | Typical use |
|---------------|----------|-------------|
| `chat_completions` | OpenAI Chat Completions | OpenAI, Gemini (OpenAI-compat), Ollama, OpenRouter, vLLM, LiteLLM |
| `responses` | OpenAI Responses API | OpenAI Responses endpoints, some xAI paths |
| `messages` | Anthropic Messages API | Claude |

## Registration

```python
from xg_agent_sdk import register_model, anthropic_claude, openai_gpt, ollama_local

register_model(**anthropic_claude(name="claude", model="claude-sonnet-4"))
register_model(**openai_gpt(name="openai", model="gpt-4o"))
register_model(**ollama_local(name="ollama", model="qwen2.5-coder"))
```

```python
register_model(
    name="custom",
    model="my-model-id",
    base_url="https://api.example.com/v1",
    api_backend="chat_completions",
    env_key="MY_API_KEY",
    context_window=128_000,
    config_path=None,  # default: ~/.grok/config.toml
    backup=True,
)
```

Use `config_path` for isolated configs (tests, CI). Prefer `env_key` over embedding secrets in `api_key`.

## Presets

| Helper | Default backend | Default env |
|--------|-----------------|-------------|
| `xai_grok` | `responses` | `XAI_API_KEY` |
| `anthropic_claude` | `messages` | `ANTHROPIC_API_KEY` |
| `openai_gpt` | `chat_completions` | `OPENAI_API_KEY` |
| `gemini_openai_compat` | `chat_completions` | `GOOGLE_API_KEY` |
| `ollama_local` | `chat_completions` | — |
| `openrouter` | `chat_completions` | `OPENROUTER_API_KEY` |

## Notes

- Tool-calling quality depends on the model; prefer stronger models for multi-step agent work.
- `register_model` creates a timestamped `.bak` backup when updating an existing config file.
- Do not commit config files that contain API keys.
