#!/bin/bash
# Setup script: copies Skill and MCP config to the parent directory
# so Claude Code discovers the skill from the parent workspace.
#
# Usage: cd tilelang-operator-dev && bash setup.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_NAME="run-tilelang-mcp"

# Create parent .claude/skills/
mkdir -p "$PARENT_DIR/.claude/skills/$SKILL_NAME"

# Copy SKILL.md
cp "$SCRIPT_DIR/.claude/skills/$SKILL_NAME/SKILL.md" "$PARENT_DIR/.claude/skills/$SKILL_NAME/"

# Copy .mcp.json (adjust path to point into this repo)
sed "s|\${workspaceFolder}/scripts|\${workspaceFolder}/tilelang-operator-dev/scripts|g" \
    "$SCRIPT_DIR/resources/.mcp.json" > "$PARENT_DIR/.mcp.json"

echo "Done! Skill installed to: $PARENT_DIR/.claude/skills/$SKILL_NAME/"
echo "MCP config written to:    $PARENT_DIR/.mcp.json"
echo ""
echo "You can now run 'claude' from: $PARENT_DIR/"
