#!/bin/bash
export PATH="$HOME/.local/bin:$PATH"
# Protocol Artifact Validation Hook for Kimi Code CLI
# Event: PreToolUse (matcher: Shell)
# Intercepts git commit in protocol-managed repos to validate artifacts.
# Kimi hook protocol: JSON via stdin, block via exit 2 + stderr, or structured JSON.

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Only trigger on Shell tool with git commit command
if [ "$TOOL" != "Shell" ]; then
  exit 0
fi

# Check if command contains git commit (but not git commit --amend or other non-standard)
if ! echo "$TOOL_INPUT" | grep -qE 'git (add.*&&.*git )?commit'; then
  exit 0
fi

# Governance-repo: from env $IWE_GOVERNANCE_REPO (default DS-strategy).
# Workspace: from env $IWE_WORKSPACE (default ~/IWE).
GOV_REPO="${IWE_GOVERNANCE_REPO:-DS-strategy}"
WORKSPACE="${IWE_WORKSPACE:-$HOME/IWE}"
GOV_PATH="$WORKSPACE/$GOV_REPO"

# Check if we're in governance repo (protocol-managed)
if ! echo "$TOOL_INPUT" | grep -q 'DayPlan\|day-open\|day-close\|WeekPlan'; then
  # Also check pwd context — look for staged DayPlan files
  STAGED=$(cd "$GOV_PATH" 2>/dev/null && git diff --cached --name-only 2>/dev/null || echo "")
  if ! echo "$STAGED" | grep -qE 'DayPlan|WeekPlan'; then
    exit 0
  fi
fi

# --- DayPlan Validation ---
DAYPLAN=$(ls "$GOV_PATH"/current/DayPlan\ *.md 2>/dev/null | head -1)

if [ -z "$DAYPLAN" ]; then
  exit 0
fi

# Required sections (parameterized — update this list when format changes)
SECTIONS=(
  "План на сегодня"
  "Календарь"
  "IWE за ночь"
  "Наработки Scout"
  "Разбор заметок"
  "Итоги вчера"
)

MISSING=()
for section in "${SECTIONS[@]}"; do
  if ! grep -q "$section" "$DAYPLAN"; then
    MISSING+=("$section")
  fi
done

# Check mandatory format elements
ERRORS=()

# --- Check 1: collapsible <details> blocks ---
DETAILS_COUNT=$(grep -c '<details' "$DAYPLAN" 2>/dev/null || echo 0)
if [ "$DETAILS_COUNT" -lt 3 ]; then
  ERRORS+=("Collapsible секции (<details>) < 3 найдено: $DETAILS_COUNT. DayPlan должен иметь collapsible-структуру")
fi

# --- Check 2: non-empty mandatory sections ---
# Календарь: должна содержать хотя бы одну строку с | (таблица) или "нет событий"
CALENDAR_CONTENT=$(awk '/Календарь/,/^<\/details>/' "$DAYPLAN" 2>/dev/null | wc -l || echo 0)
if [ "$CALENDAR_CONTENT" -lt 3 ]; then
  ERRORS+=("Секция 'Календарь' пустая или слишком короткая (${CALENDAR_CONTENT} строк)")
fi

# Scout: должна содержать хотя бы упоминание находок или "нет находок"
if ! awk '/Наработки Scout/,/^<\/details>/' "$DAYPLAN" 2>/dev/null | grep -qE 'наход|capture|статус|нет|find'; then
  ERRORS+=("Секция 'Наработки Scout' пустая")
fi

# --- Check 3: multiplier format ---
if ! grep -qE "~[0-9]+\.?[0-9]*x" "$DAYPLAN"; then
  ERRORS+=("Мультипликатор не найден — нужен формат '~N.Nx' в строке бюджета")
fi

# --- Check 4 (legacy): mandatory check and budget ---
if ! grep -qi "mandatory" "$DAYPLAN"; then
  ERRORS+=("Mandatory check (WP-7 + контентный РП) не найден")
fi

if ! grep -qE "~[0-9]+\.?[0-9]*h РП" "$DAYPLAN"; then
  ERRORS+=("Бюджет дня не в формате '~Xh РП / ~Yh физ'")
fi

# --- Check 5: Carry-over quote (if previous DayPlan exists) ---
PREV_DAYPLAN=$(ls "$GOV_PATH"/current/DayPlan\ *.md 2>/dev/null | sort | tail -2 | head -1)
if [ -n "$PREV_DAYPLAN" ] && [ "$PREV_DAYPLAN" != "$DAYPLAN" ]; then
  if ! grep -qiE 'carry.over|carry_over' "$DAYPLAN"; then
    ERRORS+=("Carry-over цитата из предыдущего Day Close отсутствует (предыдущий DayPlan: $(basename "$PREV_DAYPLAN"))")
  fi
fi

# Report results
if [ ${#MISSING[@]} -gt 0 ] || [ ${#ERRORS[@]} -gt 0 ]; then
  MISSING_STR=$(printf ', %s' "${MISSING[@]}")
  MISSING_STR=${MISSING_STR:2}
  ERRORS_STR=$(printf ', %s' "${ERRORS[@]}")
  ERRORS_STR=${ERRORS_STR:2}

  MSG="⛔ DAYPLAN VALIDATION FAILED."
  [ ${#MISSING[@]} -gt 0 ] && MSG="$MSG Пропущены секции (${#MISSING[@]}): $MISSING_STR."
  [ ${#ERRORS[@]} -gt 0 ] && MSG="$MSG Ошибки формата/структуры: $ERRORS_STR."
  MSG="$MSG Исправь DayPlan перед коммитом."

  # Kimi: block via exit 2 + stderr
  echo "$MSG" >&2
  exit 2
else
  echo "✅ DayPlan прошёл валидацию: секции, collapsible, непустые блоки, мультипликатор, carry-over."
fi

exit 0
