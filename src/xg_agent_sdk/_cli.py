"""Resolve the Grok Build CLI binary."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from .errors import CLINotFoundError

# SDK-managed install (from ``xg-agent-install-grok`` / install_cli)
_SDK_BIN = Path.home() / ".local" / "share" / "xg-agent-sdk" / "bin" / (
    "grok.exe" if os.name == "nt" else "grok"
)

# Common install locations used by x.ai/cli installers
_CANDIDATE_PATHS = (
    _SDK_BIN,
    Path.home() / ".grok" / "bin" / ("grok.exe" if os.name == "nt" else "grok"),
    Path.home() / ".local" / "bin" / ("grok.exe" if os.name == "nt" else "grok"),
    Path("/usr/local/bin/grok"),
)


def try_resolve_cli_path(cli_path: str | Path | None = None) -> str | None:
    """Like :func:`resolve_cli_path` but returns None instead of raising."""
    try:
        return resolve_cli_path(cli_path)
    except CLINotFoundError:
        return None


def resolve_cli_path(
    cli_path: str | Path | None = None,
    *,
    auto_install: bool = False,
) -> str:
    """Return an absolute path to the ``grok`` executable.

    Resolution order:
    1. Explicit ``cli_path`` argument
    2. ``GROK_CLI_PATH`` environment variable
    3. SDK-managed install (``~/.local/share/xg-agent-sdk/bin/grok``)
    4. ``PATH`` lookup for ``grok``
    5. Well-known install directories (``~/.grok/bin``, …)
    6. If ``auto_install`` (or env ``XG_AGENT_AUTO_INSTALL_CLI=1``), download a
       compatible CLI via :func:`xg_agent_sdk.install_cli.ensure_cli`
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

    # Prefer SDK-managed install before PATH so [grok] installs win
    if _SDK_BIN.is_file() and os.access(_SDK_BIN, os.X_OK):
        return str(_SDK_BIN.resolve())

    which = shutil.which("grok")
    if which:
        return which

    for candidate in _CANDIDATE_PATHS:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate.resolve())

    do_auto = auto_install or os.environ.get("XG_AGENT_AUTO_INSTALL_CLI", "").strip() in (
        "1",
        "true",
        "yes",
    )
    if do_auto:
        from .install_cli import InstallError, ensure_cli

        try:
            return ensure_cli()
        except InstallError as exc:
            raise CLINotFoundError(
                f"Grok Build CLI not found and auto-install failed: {exc}"
            ) from exc

    raise CLINotFoundError(
        "Grok Build CLI not found.\n"
        "Install a compatible CLI with one of:\n"
        "  pip install \"xg-agent-sdk[grok]\" && xg-agent-install-grok\n"
        "  python -m xg_agent_sdk.install_cli\n"
        "  curl -fsSL https://x.ai/cli/install.sh | bash\n"
        "Or set GROK_CLI_PATH / XGAgentOptions(cli_path=...)."
    )
