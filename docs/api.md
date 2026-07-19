# API reference

## `query(*, prompt, options=None)`

Run a single agent turn. Yields a stream of `Message` objects.

```python
async for message in query(prompt="...", options=XGAgentOptions(...)):
    ...
```

## `XGSDKClient(options=None)`

Stateful multi-turn client. Each turn spawns Grok Build with `--resume` after the first result.

| Method / property        | Description                                      |
|--------------------------|--------------------------------------------------|
| `await query(prompt)`    | Queue a user message                             |
| `receive_response()`     | Async iterator of messages for the queued prompt |
| `ask(prompt)`            | `query` + `receive_response` in one call         |
| `session_id`             | Last known session UUID                          |
| `await close()`          | Release client state                             |

Supports `async with XGSDKClient(...) as client:`.

## Helpers

| Function                         | Description                                      |
|----------------------------------|--------------------------------------------------|
| `await collect_result(prompt, options=None)` | Return the final `ResultMessage`      |
| `await collect_text(prompt, options=None)`   | Return final assistant text as `str`  |

## Models

| Function | Description |
|----------|-------------|
| `register_model(name, *, model, base_url, ...)` | Merge a `[model.<name>]` section into Grok config |
| `list_registered_models(config_path=None)` | List custom model names from config |

Provider presets (kwargs for `register_model`): `anthropic_claude`, `openai_gpt`, `gemini_openai_compat`, `ollama_local`, `openrouter`, `xai_grok`.

## Messages

| Type | Fields |
|------|--------|
| `TextMessage` | `text` |
| `ThoughtMessage` | `text` |
| `ResultMessage` | `result`, `stop_reason`, `session_id`, `request_id`, `usage`, `num_turns`, `total_cost_usd`, `model_usage` |
| `ErrorMessage` | `message` |
| `SystemMessage` | `subtype`, `data` (forward-compatible events) |

## Grok Build CLI install

| Command | Description |
|---------|-------------|
| `pip install "xg-agent-sdk[grok]"` | Install the SDK (then run the installer) |
| `xg-agent-install-grok` | Download a compatible Grok Build binary |
| `python -m xg_agent_sdk install-cli` | Same as above |
| `install_grok_cli()` / `ensure_cli()` | Programmatic install |

| Option / env | Description |
|--------------|-------------|
| `XGAgentOptions(auto_install_cli=True)` | Download CLI on first use if missing |
| `XG_AGENT_AUTO_INSTALL_CLI=1` | Same, via environment |

Binary location: `~/.local/share/xg-agent-sdk/bin/grok` (also linked to `~/.grok/bin`).

## Errors

| Exception | When |
|-----------|------|
| `XGSDKError` | Base class |
| `CLINotFoundError` | `grok` binary not found |
| `CLIConnectionError` | Process spawn/IO failure |
| `ProcessError` | Non-zero exit (`exit_code`, `stderr`) |
| `CLIJSONDecodeError` | Invalid streaming-json line |

## `XGAgentOptions`

See the [README configuration table](../README.md#configuration-reference) for the full CLI mapping. Notable fields:

| Field | Purpose |
|-------|---------|
| `system_prompt` / `system_prompt_file` | Replace the default system prompt |
| `rules` / `append_system_prompt` / `rules_file` | Append instructions to the default prompt |
| `model`, `cwd`, `max_turns` | Model, workspace, turn limit |
| `allowed_tools`, `disallowed_tools` | Tool filtering |
| `permission_mode`, `always_approve`, `allow`, `deny` | Permissions |
| `resume`, `continue_session`, `session_id` | Sessions |
| `cli_path`, `env`, `extra_args` | Process control |
