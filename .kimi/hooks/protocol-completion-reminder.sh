#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
# Protocol Completion Reminder Hook for Kimi Code CLI
# Event: PostToolUse (matcher: ReadFile | Skill)
# After reading a protocol or calling a skill — reminds to complete all steps.
# Kimi hook protocol: JSON via stdin, context via stdout.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.path // empty')
SKILL_NAME=$(echo "$INPUT" | jq -r '.tool_input.skill // empty')

# Trigger on reading protocols (ReadFile protocol-*.md)
if [ "$TOOL" = "ReadFile" ] && echo "$FILE_PATH" | grep -q "protocol-"; then
  PROTOCOL_NAME=$(basename "$FILE_PATH" .md)
  echo "📝 ПРОТОКОЛ ЗАГРУЖЕН: $PROTOCOL_NAME. ОБЯЗАТЕЛЬНО: (1) Выполни ВСЕ шаги алгоритма. (2) После завершения запусти /verify для верификации по чеклисту (Haiku R23). НЕ пропускай верификацию."

# Trigger on calling protocol skills (Skill tool)
elif [ "$TOOL" = "Skill" ] && echo "$SKILL_NAME" | grep -qE '^(day-open|day-close|run-protocol|wp-new)$'; then
  echo "📝 СКИЛЛ ЗАГРУЖЕН: $SKILL_NAME. ОБЯЗАТЕЛЬНО: (1) Используй SetTodoList — создай таск-лист ВСЕХ шагов скилла ДО начала исполнения. (2) Выполни ВСЕ шаги последовательно, отмечая каждый. (3) После завершения запусти /verify (Haiku R23). НЕ пропускай шаги и верификацию."

fi

exit 0
