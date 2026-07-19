"""Register custom models into Grok Build config (multi-provider)."""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

ApiBackend = Literal["chat_completions", "responses", "messages"]

_DEFAULT_CONFIG = Path.home() / ".grok" / "config.toml"
_SECTION_RE_TEMPLATE = r"(?ms)^\[model\.{name}\][^\[]*"


def default_config_path() -> Path:
    return _DEFAULT_CONFIG


def list_registered_models(config_path: Path | str | None = None) -> list[str]:
    """Return custom model section names from a Grok config file."""
    path = Path(config_path) if config_path else default_config_path()
    if not path.is_file():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    models: list[str] = []
    for key, value in data.items():
        if key.startswith("model.") and isinstance(value, dict):
            models.append(key[len("model.") :])
        # tomllib may nest under "model" table if written as [model.name]
    # Also handle nested form: data["model"]["name"] if any
    nested = data.get("model")
    if isinstance(nested, dict):
        for name, body in nested.items():
            if isinstance(body, dict) and name not in models:
                models.append(name)
    return sorted(set(models))


def register_model(
    name: str,
    *,
    model: str,
    base_url: str,
    api_backend: ApiBackend = "chat_completions",
    env_key: str | list[str] | None = None,
    api_key: str | None = None,
    extra_headers: dict[str, str] | None = None,
    context_window: int | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    max_completion_tokens: int | None = None,
    display_name: str | None = None,
    description: str | None = None,
    config_path: Path | str | None = None,
    backup: bool = True,
    extra_fields: dict[str, Any] | None = None,
) -> Path:
    """Merge a ``[model.<name>]`` section into Grok Build's config.toml.

    By default writes to ``~/.grok/config.toml`` and creates a timestamped
    ``.bak`` backup when the file already exists.

    Returns the path written.
    """
    if not name or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError(
            f"Invalid model name {name!r}; use letters, digits, _ . - only"
        )
    if api_backend not in ("chat_completions", "responses", "messages"):
        raise ValueError(f"Unsupported api_backend: {api_backend}")

    path = Path(config_path) if config_path else default_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fields: dict[str, Any] = {
        "model": model,
        "base_url": base_url,
        "api_backend": api_backend,
    }
    if display_name:
        fields["name"] = display_name
    if description:
        fields["description"] = description
    if env_key is not None:
        fields["env_key"] = env_key
    if api_key is not None:
        fields["api_key"] = api_key
    if extra_headers:
        fields["extra_headers"] = extra_headers
    if context_window is not None:
        fields["context_window"] = context_window
    if temperature is not None:
        fields["temperature"] = temperature
    if top_p is not None:
        fields["top_p"] = top_p
    if max_completion_tokens is not None:
        fields["max_completion_tokens"] = max_completion_tokens
    if extra_fields:
        fields.update(extra_fields)

    section = _format_model_section(name, fields)

    if path.is_file():
        if backup:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            bak = path.with_suffix(path.suffix + f".bak.{stamp}")
            shutil.copy2(path, bak)
        existing = path.read_text(encoding="utf-8")
        new_text = _upsert_model_section(existing, name, section)
    else:
        new_text = (
            "# Managed in part by xg-agent-sdk\n\n" + section + "\n"
        )

    # Atomic-ish write
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(new_text, encoding="utf-8")
    tmp.replace(path)
    return path


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        escaped = (
            value.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )
        return f'"{escaped}"'
    if isinstance(value, list):
        inner = ", ".join(_format_toml_value(v) for v in value)
        return f"[{inner}]"
    if isinstance(value, dict):
        # inline table
        parts = [f"{k} = {_format_toml_value(v)}" for k, v in value.items()]
        return "{ " + ", ".join(parts) + " }"
    raise TypeError(f"Cannot encode TOML value of type {type(value)}: {value!r}")


def _format_model_section(name: str, fields: dict[str, Any]) -> str:
    lines = [f"[model.{name}]"]
    for key, value in fields.items():
        lines.append(f"{key} = {_format_toml_value(value)}")
    return "\n".join(lines) + "\n"


def _upsert_model_section(existing: str, name: str, section: str) -> str:
    # Match [model.name] until next top-level [section] or EOF
    pattern = re.compile(
        rf"(?ms)^\[model\.{re.escape(name)}\]\s*\n(?:(?!^\[).*\n?)*"
    )
    if pattern.search(existing):
        # Ensure trailing newline between sections
        replacement = section if section.endswith("\n") else section + "\n"
        return pattern.sub(replacement, existing, count=1)

    body = existing.rstrip() + "\n\n" + section
    if not body.endswith("\n"):
        body += "\n"
    return body
