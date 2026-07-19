"""``python -m xg_agent_sdk`` entry."""

from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] in {"install-cli", "install-grok", "install"}:
        from .install_cli import main as install_main

        return install_main(sys.argv[2:])
    print(
        "xg-agent-sdk — agents on the Grok Build harness\n\n"
        "Commands:\n"
        "  python -m xg_agent_sdk install-cli   Install a compatible Grok Build CLI\n"
        "  xg-agent-install-grok                Same (console script)\n\n"
        "Docs: https://github.com/manick2411/xg-agent-sdk\n",
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
