"""Provider presets for :func:`register_model`.

Each helper returns kwargs suitable for ``register_model(**preset(...))``.
API keys should come from environment variables, not hard-coded strings.
"""

from __future__ import annotations

from typing import Any


def xai_grok(
    *,
    name: str = "xai-grok",
    model: str = "grok-4.5",
    base_url: str = "https://api.x.ai/v1",
    env_key: str | list[str] = "XAI_API_KEY",
    api_backend: str = "responses",
    **kwargs: Any,
) -> dict[str, Any]:
    """xAI Grok models (default Grok Build path often already covers these)."""
    return {
        "name": name,
        "model": model,
        "base_url": base_url,
        "api_backend": api_backend,
        "env_key": env_key,
        "display_name": kwargs.pop("display_name", f"xAI {model}"),
        **kwargs,
    }


def anthropic_claude(
    *,
    name: str = "claude",
    model: str = "claude-opus-4-6",
    base_url: str = "https://api.anthropic.com/v1",
    env_key: str | list[str] = "ANTHROPIC_API_KEY",
    api_key_header_from_env: bool = True,
    anthropic_version: str = "2023-06-01",
    context_window: int = 200_000,
    **kwargs: Any,
) -> dict[str, Any]:
    """Anthropic Claude via the Messages API backend.

    Grok Build uses ``extra_headers`` for ``x-api-key`` rather than Bearer.
    If ``api_key_header_from_env`` is True, we set ``env_key`` so Grok can
    resolve the key; also pass version header. For pure header-based auth,
    set ``extra_headers`` yourself after calling this helper.
    """
    extra_headers = dict(kwargs.pop("extra_headers", None) or {})
    extra_headers.setdefault("anthropic-version", anthropic_version)
    # Prefer env_key + Grok's credential resolution when possible; some
    # Anthropic setups need x-api-key. Users can set:
    #   extra_headers={"x-api-key": "..."}  or use a gateway.
    result: dict[str, Any] = {
        "name": name,
        "model": model,
        "base_url": base_url,
        "api_backend": "messages",
        "env_key": env_key,
        "extra_headers": extra_headers,
        "context_window": context_window,
        "display_name": kwargs.pop("display_name", f"Claude ({model})"),
        **kwargs,
    }
    return result


def openai_gpt(
    *,
    name: str = "openai",
    model: str = "gpt-4o",
    base_url: str = "https://api.openai.com/v1",
    env_key: str | list[str] = "OPENAI_API_KEY",
    api_backend: str = "chat_completions",
    **kwargs: Any,
) -> dict[str, Any]:
    """OpenAI Chat Completions (or set api_backend='responses')."""
    return {
        "name": name,
        "model": model,
        "base_url": base_url,
        "api_backend": api_backend,
        "env_key": env_key,
        "display_name": kwargs.pop("display_name", f"OpenAI {model}"),
        **kwargs,
    }


def gemini_openai_compat(
    *,
    name: str = "gemini",
    model: str = "gemini-2.5-pro",
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
    env_key: str | list[str] = "GOOGLE_API_KEY",
    **kwargs: Any,
) -> dict[str, Any]:
    """Google Gemini via OpenAI-compatible Chat Completions endpoint.

    Google's OpenAI-compat surface evolves; override ``base_url`` / ``model``
    if your account uses a different path. OpenRouter/LiteLLM are alternatives.
    """
    return {
        "name": name,
        "model": model,
        "base_url": base_url,
        "api_backend": "chat_completions",
        "env_key": env_key,
        "display_name": kwargs.pop("display_name", f"Gemini {model}"),
        **kwargs,
    }


def ollama_local(
    *,
    name: str = "ollama",
    model: str = "qwen2.5-coder",
    host: str = "http://localhost:11434/v1",
    **kwargs: Any,
) -> dict[str, Any]:
    """Local Ollama OpenAI-compatible server (no API key required)."""
    return {
        "name": name,
        "model": model,
        "base_url": host,
        "api_backend": "chat_completions",
        "display_name": kwargs.pop("display_name", f"Ollama {model}"),
        **kwargs,
    }


def openrouter(
    *,
    name: str = "openrouter",
    model: str = "anthropic/claude-sonnet-4",
    base_url: str = "https://openrouter.ai/api/v1",
    env_key: str | list[str] = "OPENROUTER_API_KEY",
    **kwargs: Any,
) -> dict[str, Any]:
    """OpenRouter — one key, many models (Claude, GPT, Gemini, etc.)."""
    return {
        "name": name,
        "model": model,
        "base_url": base_url,
        "api_backend": "chat_completions",
        "env_key": env_key,
        "display_name": kwargs.pop("display_name", f"OpenRouter {model}"),
        **kwargs,
    }
