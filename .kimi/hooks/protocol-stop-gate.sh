#!/bin/bash
# Protocol Stop Gate for Kimi Code CLI (v2 — blocking via context.jsonl parsing)
# Event: Stop
# Checks: if protocol skill was called in session, TodoWrite with >=3 items must exist.
# Blocks session end if protocol skill was invoked without proper TodoWrite.
#
# Uses context.jsonl as transcript equivalent (Kimi does not provide transcript_path).

set -uo pipefail
export PATH="/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:${PATH:-}"

# --- Infinite loop guard ---
if [ "${STOP_HOOK_ACTIVE:-}" = "1" ]; then
  exit 0
fi
export STOP_HOOK_ACTIVE=1

INPUT=$(cat)
if [ -z "$INPUT" ]; then
  exit 0
fi

IWE_ROOT="${IWE_ROOT:-$HOME/projects/IWE}"
GATE_LOG="$IWE_ROOT/.kimi/logs/gate_log.jsonl"
mkdir -p "$(dirname "$GATE_LOG")" 2>/dev/null || true

# --- Parse input and analyze context.jsonl via python3 ---
GATE_LOG="$GATE_LOG" python3 -c "
import json, sys, os, datetime

skill_names = {'day-open', 'day-close', 'run-protocol', 'wp-new'}
protocol_skill_found = False
max_todo_count = 0
session_id = ''

# Parse stdin JSON
stdin_data = sys.stdin.read().strip()
if not stdin_data:
    sys.exit(0)

try:
    hook_input = json.loads(stdin_data)
except json.JSONDecodeError:
    sys.exit(0)

session_id = hook_input.get('session_id', '')
if not session_id:
    sys.exit(0)

# Find session directory
import subprocess
result = subprocess.run(
    ['find', os.path.expanduser('~/.kimi/sessions'), '-type', 'd', '-name', session_id],
    capture_output=True, text=True
)
session_dir = result.stdout.strip().split('\n')[0] if result.stdout.strip() else ''

if not session_dir or not os.path.isdir(session_dir):
    sys.exit(0)

context_file = os.path.join(session_dir, 'context.jsonl')
if not os.path.isfile(context_file):
    sys.exit(0)

# Parse context.jsonl
try:
    with open(context_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if msg.get('role') != 'assistant':
                continue
            
            tool_calls = msg.get('tool_calls', [])
            if not isinstance(tool_calls, list):
                continue
            
            for tc in tool_calls:
                func = tc.get('function', {})
                name = func.get('name', '')
                args_str = func.get('arguments', '{}')
                
                try:
                    args = json.loads(args_str) if isinstance(args_str, str) else args_str
                except json.JSONDecodeError:
                    args = {}
                
                if name == 'Skill':
                    skill_name = args.get('skill', '')
                    if skill_name in skill_names:
                        protocol_skill_found = True
                
                if name == 'SetTodoList':
                    todos = args.get('todos', [])
                    if isinstance(todos, list):
                        count = len(todos)
                        if count > max_todo_count:
                            max_todo_count = count
except Exception as e:
    # Fail open on any error
    sys.exit(0)

# Log
threshold = 3
fired = protocol_skill_found and max_todo_count < threshold

try:
    log_entry = {
        'ts': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'gate': 'protocol-stop-gate',
        'session_id': session_id,
        'protocol_skill_found': protocol_skill_found,
        'todo_max': max_todo_count,
        'threshold': threshold,
        'fired': fired,
        'action': 'block' if fired else 'pass'
    }
    gate_log_path = os.environ.get('GATE_LOG', os.path.expanduser('~/projects/IWE/.kimi/logs/gate_log.jsonl'))
    os.makedirs(os.path.dirname(gate_log_path), exist_ok=True)
    with open(gate_log_path, 'a') as lf:
        lf.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
except Exception:
    pass

# Block if needed
if fired:
    msg = f'''⛔ PROTOCOL-STOP-GATE [BLOCK]: Скилл протокола был вызван, но SetTodoList с ≥{threshold} задачами не найден (найдено: {max_todo_count}).

Требования:
1. Создай SetTodoList со ВСЕМИ шагами протокола ДО начала исполнения.
2. Выполни каждый шаг, отмечая статус.
3. Только после завершения всех шагов — завершай сессию.

Действие: продолжи исполнение протокола.'''
    print(msg, file=sys.stderr)
    sys.exit(2)
" <<< "$INPUT"

exit $?
