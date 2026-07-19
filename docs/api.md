# API overview

## `query(prompt, options=None)`

Async generator of `Message` values for a single agent run.

## `XGSDKClient(options=None)`

Multi-turn client. Methods:

- `await client.query(prompt)` then `async for m in client.receive_response()`
- `async for m in client.ask(prompt)` — combined
- `client.session_id` — last known session UUID

## `collect_result` / `collect_text`

Convenience wrappers that consume the stream and return the final result.

## `register_model` / `list_registered_models`

Config helpers for multi-provider models.

## Messages

- `TextMessage` — assistant text chunk
- `ThoughtMessage` — reasoning chunk
- `ResultMessage` — final turn (text, session_id, usage, cost)
- `ErrorMessage` — agent/stream error event
- `SystemMessage` — unknown/lifecycle events (`subtype`, `data`)

## Errors

- `CLINotFoundError`
- `CLIConnectionError`
- `ProcessError` (`exit_code`, `stderr`)
- `CLIJSONDecodeError` (`line`)
