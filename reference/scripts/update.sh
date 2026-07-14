#!/usr/bin/env bash
# Sap-btp-agent & plugin auto-update — tu dong update moi nhat tu GitHub Releases
set -euo pipefail

REPO="StormShynn/sap-abap-agent"
API_URL="https://api.github.com/repos/$REPO/releases"

echo "=== SAP ABAP Agent — Auto Update ==="

# 1. Git pull plugin
echo "[1/3] Git pull plugin..."
if command -v git &>/dev/null && [ -d .git ]; then
    git pull --rebase && echo "  OK Plugin updated" || echo "  !! Git pull failed"
else
    PLUGIN_DIR="$HOME/.claude/plugins/sap-abap-agent"
    echo "  Not a git repo — cloning to $PLUGIN_DIR ..."
    if [ -d "$PLUGIN_DIR" ]; then
        (cd "$PLUGIN_DIR" && git pull)
    else
        git clone "https://github.com/$REPO.git" "$PLUGIN_DIR"
        echo "  Plugin cloned. Run: claude plugin install $PLUGIN_DIR"
    fi
fi

# 2. Fetch latest wheel
echo "[2/3] Fetch latest release..."
LATEST=$(curl -sL "$API_URL" | python3 -c "
import json, sys
releases = json.load(sys.stdin)
mcp = [r for r in releases if r['tag_name'].startswith('mcp-server-v')]
if not mcp:
    sys.exit(1)
r = mcp[0]
version = r['tag_name'].replace('mcp-server-v', '')
wheel = f'sap_abap_agent_mcp-{version}-py3-none-any.whl'
for a in r['assets']:
    if a['name'] == wheel:
        print(a['browser_download_url'])
        print(version)
        break
")

WHEEL_URL=$(echo "$LATEST" | head -1)
WHEEL_VER=$(echo "$LATEST" | tail -1)

if [ -z "$WHEEL_URL" ]; then
    echo "  !! Wheel not found in latest release"
    exit 1
fi

TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

echo "  Downloading sap_abap_agent_mcp-${WHEEL_VER} ..."
curl -sL "$WHEEL_URL" -o "$TMPDIR/wheel.whl"
echo "  OK Downloaded"

# 3. pip install
echo "[3/3] pip install --upgrade ..."
pip install --upgrade "$TMPDIR/wheel.whl"
echo "  OK sap-btp-agent updated to v$WHEEL_VER"

echo ""
echo "=== Done ==="
echo "sap-btp-agent version: v$WHEEL_VER"
sap-btp-agent --help 2>/dev/null || echo "Run: sap-btp-agent --help"
