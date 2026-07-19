from __future__ import annotations

from pathlib import Path

import pytest

from xg_agent_sdk.models import list_registered_models, register_model
from xg_agent_sdk.providers import anthropic_claude, ollama_local, openai_gpt


def test_register_and_list(tmp_path: Path):
    cfg = tmp_path / "config.toml"
    register_model(
        "my-claude",
        model="claude-opus-4-6",
        base_url="https://api.anthropic.com/v1",
        api_backend="messages",
        env_key="ANTHROPIC_API_KEY",
        extra_headers={"anthropic-version": "2023-06-01"},
        context_window=200_000,
        config_path=cfg,
        backup=False,
    )
    text = cfg.read_text(encoding="utf-8")
    assert "[model.my-claude]" in text
    assert 'model = "claude-opus-4-6"' in text
    assert 'api_backend = "messages"' in text
    assert "anthropic-version" in text
    assert list_registered_models(cfg) == ["my-claude"]


def test_upsert_preserves_other_sections(tmp_path: Path):
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        '[models]\ndefault = "grok-build"\n\n[model.old]\nmodel = "x"\n'
        'base_url = "http://x"\n',
        encoding="utf-8",
    )
    register_model(
        "old",
        model="y",
        base_url="http://y",
        config_path=cfg,
        backup=True,
    )
    text = cfg.read_text(encoding="utf-8")
    assert '[models]\ndefault = "grok-build"' in text
    assert 'model = "y"' in text
    assert 'model = "x"' not in text
    # backup created
    backups = list(tmp_path.glob("config.toml.bak.*"))
    assert len(backups) == 1


def test_presets():
    claude = anthropic_claude(model="claude-sonnet-4")
    assert claude["api_backend"] == "messages"
    assert claude["model"] == "claude-sonnet-4"
    gpt = openai_gpt(model="gpt-4o")
    assert gpt["api_backend"] == "chat_completions"
    ollama = ollama_local(model="llama3")
    assert "11434" in ollama["base_url"]


def test_invalid_name(tmp_path: Path):
    with pytest.raises(ValueError):
        register_model(
            "bad name!",
            model="m",
            base_url="http://x",
            config_path=tmp_path / "c.toml",
            backup=False,
        )
