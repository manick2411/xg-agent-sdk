"""SDK / Grok Build CLI compatibility pins."""

from __future__ import annotations

# Minimum CLI version the SDK is tested against (inclusive).
MIN_CLI_VERSION = "0.2.100"

# Default install target when no version is requested: track stable channel,
# but prefer this known-good version when ``prefer_pinned=True``.
PINNED_CLI_VERSION = "0.2.103"

# Official channel / artifact endpoints (same as https://x.ai/cli/install.sh)
CHANNEL_URLS = (
    "https://x.ai/cli/stable",
    "https://storage.googleapis.com/grok-build-public-artifacts/cli/stable",
)
ARTIFACT_BASE_URLS = (
    "https://x.ai/cli",
    "https://storage.googleapis.com/grok-build-public-artifacts/cli",
)
