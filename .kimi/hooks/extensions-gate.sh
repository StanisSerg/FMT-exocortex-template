#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
# Extensions Gate for Kimi Code CLI
# Event: PreToolUse (matcher: WriteFile|StrReplaceFile)
# Blocks direct edits to platform files — redirects user to extensions/ mechanism.
#
# Protected zones (platform-space, updated by update.sh):
#   - .claude/skills/          — skills (use extensions/*.md instead)
#   - memory/protocol-*.md     — protocols (use extensions/*.md instead)
#   - memory/templates-*.md    — templates (use extensions/*.md instead)
#   - roles/*/prompts/         — role prompts (use extensions/*.md instead)
#   - .claude/settings.json    — hooks config
#   - .claude/hooks/           — hook scripts
#   - update.sh                — update mechanism
#   - update-manifest.json     — manifest
#
# Allowed zones (user-space, never updated by update.sh):
#   - extensions/              — user extensions
#   - params.yaml              — user parameters
#   - personal/                — user files
#   - DS-strategy/             — governance repo
#   - memory/MEMORY.md         — personal memory
#   - .claude/settings.local.json — personal permissions
#   - .exocortex.env           — secrets
#   - .gitignore               — safe to edit
#   - KIMI.md, CLAUDE.md       — context files

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.path // empty')

# Only trigger on file write/edit tools
if [ "$TOOL" != "WriteFile" ] && [ "$TOOL" != "StrReplaceFile" ]; then
  exit 0
fi

# No path — skip (shouldn't happen, but guard)
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalize path: resolve relative to cwd if needed
if ! echo "$FILE_PATH" | grep -q '^/'; then
  CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
  FILE_PATH="${CWD:-$(pwd)}/$FILE_PATH"
fi

# Resolve symlinks and normalize
FILE_PATH=$(cd "$(dirname "$FILE_PATH")" 2>/dev/null && pwd)/$(basename "$FILE_PATH" 2>/dev/null) 2>/dev/null || true

# Check against protected patterns
BLOCKED=0
BLOCK_REASON=""

# Pattern 1: .claude/skills/* (platform skills)
if echo "$FILE_PATH" | grep -qE '/\.claude/skills/'; then
  BLOCKED=1
  BLOCK_REASON="Direct editing of platform skills is prohibited. Use extensions/ for customizations: create extensions/<protocol>.<hook>.md (e.g., extensions/day-close.after.md). See extensions/README.md for format."
fi

# Pattern 2: memory/protocol-*.md (platform protocols)
if echo "$FILE_PATH" | grep -qE '/memory/protocol-[^/]+\.md$'; then
  BLOCKED=1
  BLOCK_REASON="Direct editing of platform protocols is prohibited. Use extensions/ for customizations: create extensions/<protocol>.<hook>.md (e.g., extensions/protocol-close.checks.md). See extensions/README.md for format."
fi

# Pattern 3: memory/templates-*.md (platform templates)
if echo "$FILE_PATH" | grep -qE '/memory/templates-[^/]+\.md$'; then
  BLOCKED=1
  BLOCK_REASON="Direct editing of platform templates is prohibited. Use extensions/ for customizations or create personal templates in DS-strategy/."
fi

# Pattern 4: roles/*/prompts/* (role prompts)
if echo "$FILE_PATH" | grep -qE '/roles/[^/]+/prompts/'; then
  BLOCKED=1
  BLOCK_REASON="Direct editing of role prompts is prohibited. Use extensions/ for customizations or create personal role overrides in DS-strategy/."
fi

# Pattern 5: .claude/settings.json (hooks config)
if echo "$FILE_PATH" | grep -qE '/\.claude/settings\.json$'; then
  BLOCKED=1
  BLOCK_REASON="Editing .claude/settings.json is prohibited. For Kimi hooks — edit ~/.kimi/config.toml. For Claude hooks — this file is platform-managed."
fi

# Pattern 6: .claude/hooks/* (hook scripts, except extensions-gate itself)
if echo "$FILE_PATH" | grep -qE '/\.claude/hooks/'; then
  BLOCKED=1
  BLOCK_REASON="Editing platform hooks is prohibited. For Kimi — create custom hooks in ~/.kimi/config.toml. For Claude — these are managed by update.sh."
fi

# Pattern 7: update.sh and update-manifest.json
if echo "$FILE_PATH" | grep -qE '/(update\.sh|update-manifest\.json)$'; then
  BLOCKED=1
  BLOCK_REASON="Editing update.sh or update-manifest.json is prohibited. These are platform-managed files."
fi

# Block if matched
if [ "$BLOCKED" -eq 1 ]; then
  echo "⛔ EXTENSIONS GATE: $BLOCK_REASON" >&2
  exit 2
fi

exit 0
