#!/usr/bin/env bash
# Rsync the dev tree to a Kodi device and reload the skin. Local dev-loop tool only.
#
# Setup once: cp scripts/.deploy.env.example scripts/.deploy.env   (then edit it; it's gitignored)
# Usage:      scripts/deploy.sh [--restart]
#   --restart  Also send a SystemExec restart request via JSON-RPC after syncing (needed when addon.xml,
#              fonts, or the 16x9/ folder NAME changes - a plain ReloadSkin() isn't enough for those).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/scripts/.deploy.env"
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Missing $ENV_FILE - copy scripts/.deploy.env.example and fill in your Pi's details." >&2
    exit 1
fi
# shellcheck source=/dev/null
source "$ENV_FILE"
: "${PI_USER:?Set PI_USER in scripts/.deploy.env}"
: "${PI_HOST:?Set PI_HOST in scripts/.deploy.env}"
: "${PI_ADDONS_DIR:?Set PI_ADDONS_DIR in scripts/.deploy.env}"

echo "==> Syncing to ${PI_USER}@${PI_HOST}:${PI_ADDONS_DIR}/skin.hearthfire/"
rsync -az --delete \
    --exclude 'Textures.xbt' \
    --exclude '.git/' \
    --exclude 'scripts/' \
    --exclude 'design/' \
    --exclude 'dist/' \
    "$ROOT/" \
    "${PI_USER}@${PI_HOST}:${PI_ADDONS_DIR}/skin.hearthfire/"

echo "==> Requesting ReloadSkin() over the network (Settings > Services > Control > Allow remote control"
echo "    must be enabled on the device, and kodi-send must be installed locally)."
if command -v kodi-send >/dev/null 2>&1; then
    kodi-send --host="$PI_HOST" --action="ReloadSkin()" || \
        echo "kodi-send failed; reload manually from Settings > Interface > Skin, or restart Kodi."
else
    echo "kodi-send not found locally; reload manually, or install kodi-send (apt install kodi-eventclients-kodi-send)."
fi

if [[ "${1:-}" == "--restart" ]]; then
    echo "==> --restart requested: use Kodi's own JSON-RPC to restart the application, e.g.:"
    echo "    curl -s -X POST -H 'Content-Type: application/json' -d \\"
    echo "      '{\"jsonrpc\":\"2.0\",\"method\":\"Application.Quit\",\"id\":1}' \\"
    echo "      http://${PI_HOST}:8080/jsonrpc"
    echo "    (then restart Kodi on the device; a full addon.xml/font/folder-name change needs this, not just ReloadSkin)."
fi

echo "==> Done."
