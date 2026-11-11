#!/usr/bin/env bash
# Set up the Things MCP server for Claude Desktop on macOS.
#
#   ./setup.sh            # build venv, install, store token, smoke test, print config
#   ./setup.sh --no-token # skip the token prompt (keep whatever is in config.json)
#
# Steps:
#   1. Create .venv with uv (Python 3.12) and install this package editable.
#   2. Store the Things auth token in ~/.things-mcp/config.json (if not already set).
#   3. Run a stdio handshake smoke test (initialize + tools/list) against the
#      installed `things-mcp` console script. Pure Python, no GNU `timeout` needed.
#   4. Print the block to paste into Claude Desktop's config.
#
# Logging from the server goes to stderr and ~/.things-mcp/logs/ only.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$REPO_DIR/.venv"
PYTHON="$VENV/bin/python"
ENTRY="$VENV/bin/things-mcp"
CONFIG_DIR="$HOME/.things-mcp"
CONFIG_FILE="$CONFIG_DIR/config.json"
PY_VERSION="3.12"
ASK_TOKEN=1
[[ "${1:-}" == "--no-token" ]] && ASK_TOKEN=0

step() { printf '\n==> %s\n' "$*"; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

cd "$REPO_DIR"

# 1. venv + install -----------------------------------------------------------
command -v uv >/dev/null 2>&1 || die "uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"

step "Creating virtualenv (Python $PY_VERSION) at $VENV"
uv venv --python "$PY_VERSION" --allow-existing "$VENV"

step "Installing things-mcp (editable) with dev extras"
uv pip install --python "$PYTHON" -e ".[dev]"

[[ -x "$ENTRY" ]] || die "console script not found at $ENTRY"
MCP_VERSION="$("$PYTHON" -c 'import importlib.metadata as m; print(m.version("mcp"))')"
echo "installed mcp SDK $MCP_VERSION"

# 2. token ----------------------------------------------------------------------
step "Things authentication token"
mkdir -p "$CONFIG_DIR"
have_token=0
if [[ -f "$CONFIG_FILE" ]]; then
  if "$PYTHON" - "$CONFIG_FILE" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
sys.exit(0 if cfg.get("things_auth_token") else 1)
PY
  then have_token=1; fi
fi

if [[ $have_token -eq 1 ]]; then
  echo "token already stored in $CONFIG_FILE (left untouched)"
elif [[ $ASK_TOKEN -eq 1 ]]; then
  echo "Find it in Things -> Settings -> General -> Enable Things URLs -> Manage."
  read -r -p "Things auth token (leave blank to skip): " TOKEN
  if [[ -n "$TOKEN" ]]; then
    "$PYTHON" - "$CONFIG_FILE" "$TOKEN" <<'PY'
import json, os, sys
path, token = sys.argv[1], sys.argv[2]
cfg = {}
if os.path.exists(path):
    with open(path) as f:
        cfg = json.load(f)
cfg["things_auth_token"] = token
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
os.chmod(path, 0o600)
print(f"token saved to {path}")
PY
  else
    echo "skipped; run ./setup.sh again or ./.venv/bin/python configure_token.py later"
  fi
else
  echo "no token stored and --no-token given; URL-scheme tools will fail until one is set"
fi

# 3. smoke test -----------------------------------------------------------------
step "Running stdio handshake smoke test"
"$PYTHON" "$REPO_DIR/scripts/smoke_test.py" "$ENTRY"

# 4. Claude Desktop config -----------------------------------------------------
step "Claude Desktop configuration"
cat <<EOC
Add this to ~/Library/Application Support/Claude/claude_desktop_config.json
under "mcpServers", then restart Claude Desktop:

{
  "mcpServers": {
    "things": {
      "command": "$ENTRY",
      "args": []
    }
  }
}
EOC
cat > "$REPO_DIR/claude_desktop_snippet.json" <<EOC
{
  "mcpServers": {
    "things": {
      "command": "$ENTRY",
      "args": []
    }
  }
}
EOC
echo
echo "(also written to $REPO_DIR/claude_desktop_snippet.json)"
echo "Server logs: $CONFIG_DIR/logs/"
