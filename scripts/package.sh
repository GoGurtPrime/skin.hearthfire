#!/usr/bin/env bash
# Build the release zip: dist/skin.hearthfire-<version>.zip
#
# This deliberately never includes:
#   - Textures.xbt (a hosted repository packs media/ into this itself at publish time)
#   - design/, scripts/, .git, dist/ (not part of the addon - dev-only)
#   - any dotfiles, Zone.Identifier sidecars, or other dev cruft
#
# Usage: scripts/package.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKIN_DIR="$ROOT"
DIST_DIR="$ROOT/dist"

VERSION="$(grep -oP '(?<=<addon id="skin.hearthfire" version=")[^"]+' "$SKIN_DIR/addon.xml")"
if [[ -z "$VERSION" ]]; then
    echo "Could not read version from addon.xml" >&2
    exit 1
fi

OUT_NAME="skin.hearthfire-${VERSION}"
# Kodi's "Install from zip file" expects exactly one top-level folder matching the addon id
# (skin.hearthfire/addon.xml, not <versioned-name>/skin.hearthfire/addon.xml) - stage under that exact name.
STAGE_ROOT="$DIST_DIR/${OUT_NAME}-staging"
STAGE="$STAGE_ROOT/skin.hearthfire"
ZIP_PATH="$DIST_DIR/${OUT_NAME}.zip"

echo "==> Packaging Hearthfire v${VERSION}"
rm -rf "$STAGE_ROOT" "$ZIP_PATH"
mkdir -p "$STAGE"

rsync -a \
    --exclude 'Textures.xbt' \
    --exclude '.git/' \
    --exclude 'dist/' \
    --exclude 'scripts/' \
    --exclude 'design/' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'Thumbs.db' \
    --exclude '*:Zone.Identifier' \
    "$SKIN_DIR"/ "$STAGE/"

echo "==> Verifying no forbidden file types made it into the staged tree"
if find "$STAGE" \( -iname '*.xbt' -o -iname '*.so' -o -iname '*.dll' -o -iname '*.pyo' -o -iname '*.exe' -o -iname '*.xpr' -o -iname 'Thumbs.db' \) | grep -q .; then
    echo "ERROR: forbidden file type found in staged tree:" >&2
    find "$STAGE" \( -iname '*.xbt' -o -iname '*.so' -o -iname '*.dll' -o -iname '*.pyo' -o -iname '*.exe' -o -iname '*.xpr' -o -iname 'Thumbs.db' \) >&2
    exit 1
fi

echo "==> Verifying no files are marked executable"
if find "$STAGE" -type f -perm -u+x | grep -q .; then
    echo "WARNING: executable bit set on:" >&2
    find "$STAGE" -type f -perm -u+x >&2
    find "$STAGE" -type f -perm -u+x -exec chmod -x {} +
    echo "(cleared automatically)"
fi

echo "==> Zipping -> $ZIP_PATH"
( cd "$STAGE_ROOT" && zip -rq "$ZIP_PATH" "skin.hearthfire" )
rm -rf "$STAGE_ROOT"

SIZE_MB=$(du -m "$ZIP_PATH" | cut -f1)
echo "==> Done: $ZIP_PATH (${SIZE_MB} MB)"
if [[ "$SIZE_MB" -gt 100 ]]; then
    echo "WARNING: package exceeds the informal 100MB guidance for addon submissions." >&2
fi
