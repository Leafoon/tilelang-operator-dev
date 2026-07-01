#!/bin/bash
# Setup script: installs the TileLang Operator Dev skill and MCP config globally
# so Claude Code discovers them from any directory.
#
# Usage: cd tilelang-operator-dev && bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="tilelang-operator-dev"
MCP_SERVER="$SCRIPT_DIR/scripts/tilelang_operator_mcp.py"
MCP_CONFIG="$HOME/.claude/.mcp.json"
PYTHON_BIN="${PYTHON:-python3}"

"$PYTHON_BIN" - <<'PY'
import sys

if sys.version_info < (3, 10):
    print(
        "TileLang Operator Dev requires Python 3.10 or newer. "
        "Set PYTHON=/path/to/python3.10 when running setup.sh.",
        file=sys.stderr,
    )
    sys.exit(1)
PY

# Install the operator development skill globally.
mkdir -p "$HOME/.claude/skills/$SKILL_NAME"
cp "$SCRIPT_DIR/SKILL.md" "$HOME/.claude/skills/$SKILL_NAME/SKILL.md"

# Upsert MCP config globally without deleting other configured servers.
mkdir -p "$HOME/.claude"
MCP_CONFIG="$MCP_CONFIG" MCP_SERVER="$MCP_SERVER" MCP_COMMAND="$PYTHON_BIN" "$PYTHON_BIN" <<'PY'
import json
import os
import shutil
import time
from pathlib import Path

config_path = Path(os.environ["MCP_CONFIG"]).expanduser()
mcp_server = os.environ["MCP_SERVER"]
mcp_command = os.environ["MCP_COMMAND"]
server_name = "tilelang-operator-knowledge"

data = {}
if config_path.exists():
    backup_path = config_path.with_name(
        f"{config_path.name}.bak.{time.strftime('%Y%m%d%H%M%S')}"
    )
    shutil.copy2(config_path, backup_path)
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = {}
    except json.JSONDecodeError:
        data = {"_previous_config_backup": str(backup_path)}

mcp_servers = data.get("mcpServers")
if not isinstance(mcp_servers, dict):
    mcp_servers = {}
data["mcpServers"] = mcp_servers
mcp_servers[server_name] = {
    "command": mcp_command,
    "args": [mcp_server],
}

tmp_path = config_path.with_suffix(config_path.suffix + ".tmp")
tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
tmp_path.replace(config_path)
PY

echo "Done!"
echo "  Skill:     ~/.claude/skills/$SKILL_NAME/SKILL.md"
echo "  MCP config: ~/.claude/.mcp.json"
echo "  MCP server: $MCP_SERVER"
echo "  Python:    $PYTHON_BIN"
echo ""
echo "Restart Claude Code to pick up the changes."
