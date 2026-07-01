#!/bin/bash
# Setup script: installs the TileLang Operator Dev skill and MCP config globally
# so Claude Code discovers them from any directory.
#
# Usage: cd tilelang-operator-dev && bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="tilelang-operator-dev"
MCP_SERVER="$SCRIPT_DIR/scripts/tilelang_operator_mcp.py"

# Install the operator development skill globally.
mkdir -p "$HOME/.claude/skills/$SKILL_NAME"
cp "$SCRIPT_DIR/SKILL.md" "$HOME/.claude/skills/$SKILL_NAME/SKILL.md"

# Install MCP config globally.
cat > "$HOME/.claude/.mcp.json" << EOF
{
  "mcpServers": {
    "tilelang-operator-knowledge": {
      "command": "python3",
      "args": ["$MCP_SERVER"]
    }
  }
}
EOF

echo "Done!"
echo "  Skill:     ~/.claude/skills/$SKILL_NAME/SKILL.md"
echo "  MCP config: ~/.claude/.mcp.json"
echo "  MCP server: $MCP_SERVER"
echo ""
echo "Restart Claude Code to pick up the changes."
