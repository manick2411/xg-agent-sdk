"""XG Agent SDK — programmatic agents on the Grok Build harness.

Not an official xAI product. Wraps the open-source Grok Build CLI
(https://github.com/xai-org/grok-build) with a Claude Agent SDK–shaped API.
Inference can use Grok, Claude, OpenAI, Gemini (OpenAI-compat), Ollama, or
any endpoint Grok Build custom models support.
"""

from ._version import __version__
from .client import XGSDKClient
from .errors import (
    CLIConnectionError,
    CLIJSONDecodeError,
    CLINotFoundError,
    XGSDKError,
    ProcessError,
)
from .helpers import collect_result, collect_text
from .models import list_registered_models, register_model
from .providers import (
    anthropic_claude,
    gemini_openai_compat,
    ollama_local,
    openai_gpt,
    openrouter,
    xai_grok,
)
from .query import query
from .types import (
    ErrorMessage,
    XGAgentOptions,
    Message,
    ResultMessage,
    SystemMessage,
    TextMessage,
    ThoughtMessage,
)

__all__ = [
    "__version__",
    "query",
    "XGSDKClient",
    "XGAgentOptions",
    "Message",
    "TextMessage",
    "ThoughtMessage",
    "ResultMessage",
    "ErrorMessage",
    "SystemMessage",
    "XGSDKError",
    "CLINotFoundError",
    "CLIConnectionError",
    "ProcessError",
    "CLIJSONDecodeError",
    "register_model",
    "list_registered_models",
    "anthropic_claude",
    "openai_gpt",
    "gemini_openai_compat",
    "ollama_local",
    "openrouter",
    "xai_grok",
    "collect_result",
    "collect_text",
]
