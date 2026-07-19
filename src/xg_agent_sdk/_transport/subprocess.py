"""Async subprocess transport for ``grok -p --output-format streaming-json``."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from pathlib import Path

from .._argv import build_argv
from .._cli import resolve_cli_path
from .._parser import StreamAccumulator, parse_line
from ..errors import CLIConnectionError, ProcessError
from ..types import ErrorMessage, XGAgentOptions, Message, ResultMessage


async def run_streaming_query(
    prompt: str,
    options: XGAgentOptions | None = None,
) -> AsyncIterator[Message]:
    """Spawn Grok Build and yield parsed streaming messages."""
    options = options or XGAgentOptions()
    cli = resolve_cli_path(options.cli_path)
    argv, temp_prompt = build_argv(prompt, options, cli_path=cli)

    env = os.environ.copy()
    if options.env:
        env.update(options.env)

    try:
        try:
            proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
            )
        except FileNotFoundError as exc:
            raise CLIConnectionError(f"Failed to spawn Grok CLI: {exc}") from exc
        except OSError as exc:
            raise CLIConnectionError(f"Failed to spawn Grok CLI: {exc}") from exc

        assert proc.stdout is not None
        assert proc.stderr is not None

        accumulator = StreamAccumulator()
        stderr_chunks: list[bytes] = []

        async def _drain_stderr() -> None:
            while True:
                chunk = await proc.stderr.read(4096)
                if not chunk:
                    break
                stderr_chunks.append(chunk)

        stderr_task = asyncio.create_task(_drain_stderr())
        had_error_message = False

        try:
            while True:
                line_b = await proc.stdout.readline()
                if not line_b:
                    break
                line = line_b.decode("utf-8", errors="replace")
                message = parse_line(line)
                if message is None:
                    continue
                message = accumulator.process(message)
                if isinstance(message, ErrorMessage):
                    had_error_message = True
                yield message
        finally:
            await stderr_task
            try:
                await asyncio.wait_for(proc.wait(), timeout=30.0)
            except TimeoutError:
                proc.kill()
                await proc.wait()
                raise ProcessError(
                    "Grok Build process timed out waiting for exit",
                    exit_code=None,
                    stderr=_decode_stderr(stderr_chunks),
                ) from None

        stderr_text = _decode_stderr(stderr_chunks)
        code = proc.returncode if proc.returncode is not None else 0

        if options.raise_on_error and code != 0 and not had_error_message:
            raise ProcessError(
                f"Grok Build exited with code {code}"
                + (f": {stderr_text.strip()}" if stderr_text.strip() else ""),
                exit_code=code,
                stderr=stderr_text,
            )
        if (
            options.raise_on_error
            and code != 0
            and had_error_message
        ):
            # Error was already yielded; still raise so callers can catch
            raise ProcessError(
                f"Grok Build exited with code {code}"
                + (f": {stderr_text.strip()}" if stderr_text.strip() else ""),
                exit_code=code,
                stderr=stderr_text,
            )
    finally:
        if temp_prompt is not None:
            try:
                temp_prompt.unlink(missing_ok=True)
            except OSError:
                pass


def _decode_stderr(chunks: list[bytes]) -> str:
    return b"".join(chunks).decode("utf-8", errors="replace")
