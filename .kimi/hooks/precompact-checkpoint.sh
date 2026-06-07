#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
# PreCompact Checkpoint Hook for Kimi Code CLI
# Event: PreCompact
# Before context compaction — remind the agent to save checkpoint.
# Kimi hook protocol: JSON via stdin, context via stdout.

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
TRIGGER=$(echo "$INPUT" | jq -r '.trigger // empty')
TOKEN_COUNT=$(echo "$INPUT" | jq -r '.token_count // empty')

PROJECT_DIR="${CWD:-$(pwd)}"
CHECKPOINT_FILE="$PROJECT_DIR/.kimi/checkpoint.md"
mkdir -p "$(dirname "$CHECKPOINT_FILE")" 2>/dev/null || true

echo "⚠️ PRECOMPACT: Контекст будет сжат (trigger: $TRIGGER, tokens: $TOKEN_COUNT). Перед продолжением прочитай .kimi/checkpoint.md если он есть. Запиши в него: (1) Над каким РП работаешь, (2) Что осталось сделать, (3) Какой протокол выполняешь и на каком шаге, (4) Незавершённые шаги протокола (включая верификацию)."

exit 0
