"""Install a Grok Build CLI binary compatible with this SDK.

Mirrors the official installer layout (https://x.ai/cli/install.sh):

* Downloads ``grok-<version>-<os>-<arch>``
* Installs under ``~/.local/share/xg-agent-sdk/bin/grok`` (SDK-managed)
* Also links into ``~/.grok/bin/grok`` when possible (matches official path)

Usage::

    pip install "xg-agent-sdk[grok]"
    xg-agent-install-grok

    # or
    python -m xg_agent_sdk.install_cli
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from ._compat import (
    ARTIFACT_BASE_URLS,
    CHANNEL_URLS,
    MIN_CLI_VERSION,
    PINNED_CLI_VERSION,
)

# SDK-managed install root (always used by resolve_cli_path)
SDK_SHARE_DIR = Path.home() / ".local" / "share" / "xg-agent-sdk"
SDK_BIN_DIR = SDK_SHARE_DIR / "bin"
SDK_GROK_PATH = SDK_BIN_DIR / ("grok.exe" if os.name == "nt" else "grok")

# Official layout (optional second link)
OFFICIAL_BIN_DIR = Path.home() / ".grok" / "bin"
OFFICIAL_DOWNLOADS = Path.home() / ".grok" / "downloads"


class InstallError(RuntimeError):
    """Grok Build CLI installation failed."""


def _platform_triple() -> tuple[str, str, str]:
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        os_name = "macos"
    elif system == "Linux":
        os_name = "linux"
    elif system == "Windows" or os.name == "nt":
        os_name = "windows"
    else:
        raise InstallError(f"Unsupported OS: {system}")

    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "aarch64"
    else:
        raise InstallError(f"Unsupported architecture: {machine}")

    return os_name, arch, f"{os_name}-{arch}"


def _http_get(url: str, *, timeout: float = 60.0) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"xg-agent-sdk-install/{PINNED_CLI_VERSION}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise InstallError(f"HTTP {exc.code} fetching {url}") from exc
    except urllib.error.URLError as exc:
        raise InstallError(f"Network error fetching {url}: {exc.reason}") from exc


def fetch_latest_stable_version() -> str:
    """Return the latest stable version string from the channel pointer."""
    last_err: Exception | None = None
    for url in CHANNEL_URLS:
        try:
            text = _http_get(url, timeout=30.0).decode("utf-8", errors="replace")
            version = text.strip().splitlines()[0].strip()
            if version and _is_semver(version):
                return version
        except Exception as exc:  # noqa: BLE001 — try next mirror
            last_err = exc
            continue
    raise InstallError(
        f"Could not resolve latest Grok Build version from channel URLs: {last_err}"
    )


def _is_semver(version: str) -> bool:
    parts = version.split("-", 1)[0].split(".")
    return len(parts) == 3 and all(p.isdigit() for p in parts)


def parse_version(version: str) -> tuple[int, int, int]:
    core = version.split("-", 1)[0]
    major, minor, patch = (int(x) for x in core.split("."))
    return major, minor, patch


def version_at_least(version: str, minimum: str) -> bool:
    return parse_version(version) >= parse_version(minimum)


def download_binary(version: str, dest: Path) -> Path:
    """Download the platform binary for ``version`` into ``dest`` (file path)."""
    os_name, _arch, triple = _platform_triple()
    suffix = ".exe" if os_name == "windows" else ""
    last_err: Exception | None = None

    for base in ARTIFACT_BASE_URLS:
        url = f"{base}/grok-{version}-{triple}{suffix}"
        try:
            data = _http_get(url, timeout=300.0)
            if len(data) < 1_000_000:
                # Sanity: real binaries are multi-MB
                raise InstallError(
                    f"Downloaded artifact looks too small ({len(data)} bytes) from {url}"
                )
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            return dest
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue

    raise InstallError(
        f"Failed to download Grok Build {version} for {triple}: {last_err}"
    )


def _link_or_copy(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    try:
        os.symlink(src, dest)
    except OSError:
        shutil.copy2(src, dest)
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def install_grok_cli(
    *,
    version: str | None = None,
    use_pinned: bool = True,
    link_official: bool = True,
    force: bool = False,
) -> Path:
    """Install Grok Build CLI and return the path to the ``grok`` binary.

    Args:
        version: Exact version (e.g. ``\"0.2.103\"``). If None, uses the pinned
            SDK-compatible version when ``use_pinned`` else latest stable.
        use_pinned: Prefer :data:`PINNED_CLI_VERSION` over channel latest.
        link_official: Also install under ``~/.grok/bin`` (official layout).
        force: Reinstall even if an existing binary is present.
    """
    if version is None:
        if use_pinned:
            version = PINNED_CLI_VERSION
        else:
            version = fetch_latest_stable_version()

    if not version_at_least(version, MIN_CLI_VERSION):
        raise InstallError(
            f"Grok Build {version} is older than the minimum supported "
            f"{MIN_CLI_VERSION} for this SDK."
        )

    if SDK_GROK_PATH.is_file() and not force:
        existing = _probe_version(SDK_GROK_PATH)
        if existing and version_at_least(existing, MIN_CLI_VERSION):
            return SDK_GROK_PATH

    SDK_BIN_DIR.mkdir(parents=True, exist_ok=True)
    OFFICIAL_DOWNLOADS.mkdir(parents=True, exist_ok=True)

    os_name, _arch, triple = _platform_triple()
    suffix = ".exe" if os_name == "windows" else ""
    artifact_name = f"grok-{version}-{triple}{suffix}"
    download_path = OFFICIAL_DOWNLOADS / artifact_name

    with tempfile.TemporaryDirectory(prefix="xg-agent-sdk-cli-") as tmp:
        tmp_bin = Path(tmp) / artifact_name
        print(f"Downloading Grok Build CLI {version} ({triple})...", file=sys.stderr)
        download_binary(version, tmp_bin)

        # Smoke-test
        if os_name != "windows":
            import subprocess

            try:
                subprocess.run(
                    [str(tmp_bin), "--version"],
                    check=True,
                    capture_output=True,
                    timeout=30,
                )
            except Exception as exc:  # noqa: BLE001
                raise InstallError(
                    f"Downloaded binary failed to run (--version): {exc}"
                ) from exc

        shutil.copy2(tmp_bin, download_path)
        download_path.chmod(
            download_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

    # SDK-managed path (primary for this package)
    _link_or_copy(download_path, SDK_GROK_PATH)

    if link_official:
        official = OFFICIAL_BIN_DIR / ("grok.exe" if os_name == "windows" else "grok")
        agent = OFFICIAL_BIN_DIR / ("agent.exe" if os_name == "windows" else "agent")
        _link_or_copy(download_path, official)
        _link_or_copy(download_path, agent)

    print(f"Installed Grok Build CLI {version} → {SDK_GROK_PATH}", file=sys.stderr)
    if link_official:
        print(f"Also linked → {OFFICIAL_BIN_DIR / 'grok'}", file=sys.stderr)
    print(
        "Tip: add ~/.local/share/xg-agent-sdk/bin (or ~/.grok/bin) to PATH "
        "if you want `grok` available in your shell.",
        file=sys.stderr,
    )
    return SDK_GROK_PATH


def _probe_version(path: Path) -> str | None:
    import re
    import subprocess

    try:
        out = subprocess.run(
            [str(path), "--version"],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except Exception:  # noqa: BLE001
        return None
    m = re.search(r"(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)", out.stdout or out.stderr or "")
    return m.group(1) if m else None


def ensure_cli(
    *,
    version: str | None = None,
    force: bool = False,
) -> str:
    """Return a path to a usable CLI, installing if necessary."""
    from ._cli import try_resolve_cli_path

    existing = try_resolve_cli_path()
    if existing and not force:
        ver = _probe_version(Path(existing))
        if ver is None or version_at_least(ver, MIN_CLI_VERSION):
            return existing
    path = install_grok_cli(version=version, force=force)
    return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="xg-agent-install-grok",
        description=(
            "Install a Grok Build CLI binary compatible with xg-agent-sdk "
            f"(minimum {MIN_CLI_VERSION}, default pin {PINNED_CLI_VERSION})."
        ),
    )
    parser.add_argument(
        "--version",
        dest="cli_version",
        default=None,
        help=f"Exact CLI version to install (default: pinned {PINNED_CLI_VERSION})",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Install latest stable from the official channel instead of the pin",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reinstall even if a compatible CLI is already present",
    )
    parser.add_argument(
        "--no-official-link",
        action="store_true",
        help="Do not also install under ~/.grok/bin",
    )
    args = parser.parse_args(argv)

    try:
        path = install_grok_cli(
            version=args.cli_version,
            use_pinned=not args.latest,
            link_official=not args.no_official_link,
            force=args.force,
        )
    except InstallError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
