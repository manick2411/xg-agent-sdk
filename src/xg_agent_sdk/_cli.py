"""Resolve the Grok Build CLI binary."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .errors import CLINotFoundError

# Common install locations used by x.ai/cli installers
_CANDIDATE_PATHS = (
    Path.home() / ".grok" / "bin" / "grok",
    Path.home() / ".local" / "bin" / "grok",
    Path("/usr/local/bin/grok"),
)


def resolve_cli_path(cli_path: str | Path | None = None) -> str:
    """Return an absolute path to the ``grok`` executable.

    Resolution order:
    1. Explicit ``cli_path`` argument
    2. ``GROK_CLI_PATH`` environment variable
    3. ``PATH`` lookup for ``grok``
    4. Well-known install directories
    """
    if cli_path is not None:
        path = Path(cli_path).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
        raise CLINotFoundError(f"Grok CLI not found or not executable at: {path}")

    env_path = os.environ.get("GROK_CLI_PATH")
    if env_path:
        path = Path(env_path).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
        raise CLINotFoundError(
            f"GROK_CLI_PATH is set but not an executable file: {env_path}"
        )

    which = shutil.which("grok")
    if which:
        return which

    for candidate in _CANDIDATE_PATHS:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())

    raise CLINotFoundError(
        "Grok Build CLI not found. Install it with:\n"
        "  curl -fsSL https://x.ai/cli/install.sh | bash\n"
        "Or set GROK_CLI_PATH / XGAgentOptions(cli_path=...)."
    )
