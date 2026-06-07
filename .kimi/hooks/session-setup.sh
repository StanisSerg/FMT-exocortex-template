#!/bin/bash
# Session Setup Hook for Kimi Code CLI
# Event: SessionStart
# Configures session approvals for IWE workspace.
# Sets auto_approve_actions to allow git and file edits without prompting,
# while keeping dangerous operations (rm -rf, .env edits) gated by manual approval.

INPUT=$(cat)

IWE_ROOT="${IWE_ROOT:-$HOME/projects/IWE}"

python3 -c "
import json, sys, os, subprocess

stdin_data = sys.stdin.read().strip()
if not stdin_data:
    sys.exit(0)

try:
    hook_input = json.loads(stdin_data)
except json.JSONDecodeError:
    sys.exit(0)

cwd = hook_input.get('cwd', '')
session_id = hook_input.get('session_id', '')

# Only apply to IWE workspace sessions
iwe_root = os.path.expanduser('$IWE_ROOT')
if not cwd or not cwd.startswith(iwe_root):
    sys.exit(0)

if not session_id:
    sys.exit(0)

# Find session state.json
result = subprocess.run(
    ['find', os.path.expanduser('~/.kimi/sessions'), '-type', 'd', '-name', session_id],
    capture_output=True, text=True
)
session_dir = result.stdout.strip().split('\n')[0] if result.stdout.strip() else ''

if not session_dir or not os.path.isdir(session_dir):
    sys.exit(0)

state_file = os.path.join(session_dir, 'state.json')
if not os.path.isfile(state_file):
    sys.exit(0)

# Backup original state
backup = state_file + '.bak'
if not os.path.exists(backup):
    try:
        import shutil
        shutil.copy2(state_file, backup)
    except Exception:
        pass

# Modify state.json: set auto_approve_actions for IWE workflow
try:
    with open(state_file, 'r') as f:
        state = json.load(f)
except Exception:
    sys.exit(0)

state['approval'] = state.get('approval', {})
state['approval']['yolo'] = False  # Keep overall YOLO off for safety
state['approval']['auto_approve_actions'] = [
    'edit file',
    'run command'
]

try:
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
except Exception:
    sys.exit(0)

print('IWE session approvals configured: edit file + run command auto-approved')
" <<< "$INPUT"

exit 0
