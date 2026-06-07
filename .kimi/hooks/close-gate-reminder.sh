#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
# Close Gate Reminder Hook for Kimi Code CLI (v3 — Day Close via /run-protocol)
# Event: UserPromptSubmit
# Day Close → BLOCKING instruction to call /run-protocol day-close.
# Session Close → compact checklist.
# Compatible with Kimi hooks: reads JSON from stdin, outputs context to stdout.

INPUT=$(cat)
# Sanitize multiline prompts for jq
SANITIZED=$(printf '%s' "$INPUT" | LC_ALL=C tr '\n\r\t' '   ')
PROMPT=$(printf '%s' "$SANITIZED" | jq -r '.prompt // empty' | tr '[:upper:]' '[:lower:]')

# Day Close → BLOCKING call /run-protocol
if echo "$PROMPT" | grep -qE '(итоги дня|закрываю день|закрывай день)'; then
  echo "⛔ БЛОКИРУЮЩЕЕ: Day Close выполняется ТОЛЬКО через skill /run-protocol с аргументом 'day-close'. ПЕРВОЕ И ЕДИНСТВЕННОЕ действие = вызвать Skill tool: skill='run-protocol', args='day-close'. НЕ читать protocol-close.md вручную. НЕ выполнять шаги самостоятельно. НЕ писать итоги без /run-protocol. Причина: 5 инцидентов пропуска шагов при ручном исполнении (15, 18, 19, 27 мар). /run-protocol гарантирует пошаговый TodoList + верификацию Haiku R23."

# Session Close → /run-protocol close
elif echo "$PROMPT" | grep -qE '(закрывай|закрываю|заливай|запуши|закрывай сессию)'; then
  echo "⛔ БЛОКИРУЮЩЕЕ: Session Close выполняется ТОЛЬКО через skill /run-protocol с аргументом 'close'. ПЕРВОЕ И ЕДИНСТВЕННОЕ действие = вызвать Skill tool: skill='run-protocol', args='close'. НЕ выполнять шаги самостоятельно. /run-protocol гарантирует пошаговый TodoList + верификацию."

fi

exit 0
