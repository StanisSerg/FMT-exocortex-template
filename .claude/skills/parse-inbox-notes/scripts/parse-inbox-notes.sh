#!/bin/bash
# parse-inbox-notes.sh — helper для скилла /parse-inbox-notes
# Детерминированное сканирование pending-заметок в inbox.

set -euo pipefail

REPO="${IWE_GOVERNANCE_REPO:-DS-strategy}"
WORKSPACE="${IWE_WORKSPACE:-/home/asus/IWE}"
INBOX_DIR="$WORKSPACE/$REPO/inbox"

usage() {
    echo "Usage: $0 <scan|pull>"
    echo "  scan  — вывести JSON со списком pending-заметок"
    echo "  pull  — git pull --rebase в governance-репо"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

CMD="$1"

case "$CMD" in
    pull)
        if [ ! -d "$WORKSPACE/$REPO/.git" ]; then
            echo "ERROR: $WORKSPACE/$REPO не является git-репо" >&2
            exit 1
        fi
        cd "$WORKSPACE/$REPO"
        if ! git diff --quiet || ! git diff --cached --quiet; then
            echo "ERROR: в $REPO есть незакоммиченные изменения" >&2
            exit 1
        fi
        git pull --rebase origin main
        ;;

    scan)
        python3 - "$INBOX_DIR" <<'PY'
import sys, re, json, os

inbox_dir = sys.argv[1]
results = []

def scan_captures(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    for match in re.finditer(r'^(### .*?)$', content, re.MULTILINE):
        line = match.group(1)
        if re.search(r'\[(analyzed|processed|duplicate|defer)', line):
            continue
        heading_text = re.sub(r'^###\s*', '', line).strip()
        if not heading_text or heading_text.lower() in ('captures (inbox)',):
            continue
        start = match.end()
        next_heading = re.search(r'\n##[#]?\s', content[start:])
        body = content[start:start + next_heading.start()].strip() if next_heading else content[start:].strip()
        if "**Статус:** imported" in body and "Import from fleeting-notes.md" in line:
            continue
        if not body or body.isspace():
            continue
        meta_found = any(
            re.match(r'^\*\*(Источник|Type|Тип|Source|Маркер|Trigger)', ln)
            for ln in body.splitlines()[:8]
        )
        if not meta_found:
            continue
        results.append({"source_file": "captures.md", "heading": line, "body": body[:2000]})

def scan_fleeting_notes(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Убираем frontmatter и основной заголовок
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    content = re.sub(r'^#\s+Fleeting Notes\s*\n', '', content, flags=re.IGNORECASE)
    # Разбиваем по разделителям --- и пустым строкам
    blocks = re.split(r'\n---\s*\n|\n\s*\n\s*\n', content)
    idx = 1
    for block in blocks:
        block = block.strip()
        if not block or block.isspace():
            continue
        # Пропускаем уже помеченные
        if re.search(r'\[(analyzed|processed|duplicate|defer)\s', block):
            continue
        # Используем первую непустую строку как заголовок (пропускаем остатки ---)
        lines = [l.strip() for l in block.splitlines() if l.strip() and l.strip() != '---']
        if not lines:
            continue
        heading = lines[0][:80]
        results.append({
            "source_file": "fleeting-notes.md",
            "heading": f"### Заметка {idx}: {heading}",
            "body": block[:2000]
        })
        idx += 1

captures_path = os.path.join(inbox_dir, "captures.md")
if os.path.isfile(captures_path):
    scan_captures(captures_path)

notes_path = os.path.join(inbox_dir, "fleeting-notes.md")
if os.path.isfile(notes_path):
    scan_fleeting_notes(notes_path)

print(json.dumps(results, ensure_ascii=False, indent=2))
PY
        ;;

    *)
        usage
        ;;
esac
