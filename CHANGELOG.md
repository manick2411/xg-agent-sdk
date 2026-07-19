# Changelog

## [0.1.1](https://github.com/manick2411/xg-agent-sdk/releases/tag/v0.1.1) — 2026-07-19

### Added

- `xg-agent-install-grok` / `python -m xg_agent_sdk install-cli` to download a
  Grok Build CLI binary compatible with this SDK
- Optional extra: `pip install "xg-agent-sdk[grok]"`
- `XGAgentOptions.auto_install_cli` and env `XG_AGENT_AUTO_INSTALL_CLI=1`
- Clearer CLI-not-found errors with install instructions

## [0.1.0](https://github.com/manick2411/xg-agent-sdk/releases/tag/v0.1.0) — 2026-07-19

### Added

- `query()` streaming API over Grok Build headless mode
- `XGSDKClient` for multi-turn sessions
- `XGAgentOptions` (prompts, tools, permissions, models, sandbox)
- `register_model` and provider presets
- `collect_text` / `collect_result` helpers
