#!/usr/bin/env bash
# LOCAL DEV/PERF TOOL ONLY. Packs media/ into a Textures.xbt for sideload performance testing on the Pi.
# A hosted add-on repository packs media/ itself at publish time and won't accept a pre-packed .xbt - this
# script's output must never be committed or included in scripts/package.sh's zip.
#
# Requires Kodi's TexturePacker binary on PATH. It ships with a full Kodi build (tools/depends/native/
# TexturePacker in the xbmc source tree) or as a standalone download for your platform; this script does not
# install it for you.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MEDIA_DIR="$ROOT/media"
OUT="$ROOT/Textures.xbt"

if ! command -v TexturePacker >/dev/null 2>&1; then
    echo "TexturePacker not found on PATH." >&2
    echo "Build it from https://github.com/xbmc/xbmc (tools/depends/native/TexturePacker) or grab a" >&2
    echo "platform build from the Kodi project, then re-run this script." >&2
    exit 1
fi

echo "==> Packing $MEDIA_DIR -> $OUT (dev-only; gitignored; never shipped in package.sh's zip)"
TexturePacker -input "$MEDIA_DIR" -output "$OUT" -dupecheck

echo "==> Done. Deploy with scripts/deploy.sh to sideload-test the packed build; delete $OUT before committing."
