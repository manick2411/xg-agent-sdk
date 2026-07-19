"""SDK error hierarchy."""

from __future__ import annotations


class XGSDKError(Exception):
    """Base error for the XG Agent SDK."""


class CLINotFoundError(XGSDKError):
    """The ``grok`` CLI binary was not found on PATH or at ``cli_path``."""


class CLIConnectionError(XGSDKError):
    """Failed to spawn or communicate with the Grok Build process."""


class ProcessError(XGSDKError):
    """Grok Build exited with a non-zero status."""

    def __init__(
        self,
        message: str,
        *,
        exit_code: int | None = None,
        stderr: str | None = None,
    ) -> None:
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr


class CLIJSONDecodeError(XGSDKError):
    """A streaming-json line could not be parsed as JSON."""

    def __init__(self, message: str, *, line: str | None = None) -> None:
        super().__init__(message)
        self.line = line
