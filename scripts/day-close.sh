#!/bin/bash
# day-close.sh — локальная копия с исправленным путём memory
set -euo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/IWE}"
GOVERNANCE_REPO="${GOVERNANCE_REPO:-DS-strategy}"
DS_STRATEGY="$WORKSPACE_DIR/$GOVERNANCE_REPO"
MEMORY_DIR="${MEMORY_DIR:-$WORKSPACE_DIR/memory}"
BACKUP_DIR="${BACKUP_DIR:-$WORKSPACE_DIR/exocortex}"

echo "[day-close] === Day Close (автоматические шаги) ==="

echo "[day-close] Шаг 1/3: Backup memory/ → exocortex/"
if [ -d "$MEMORY_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$MEMORY_DIR" "$BACKUP_DIR/memory-$(date +%Y%m%d-%H%M%S)"
    echo "[day-close]   backup=OK → $BACKUP_DIR"
    # Ротация: хранить только 14 последних бэкапов
    ROTATE_COUNT=14
    ROTATE_DELETED=$(ls -1dt "$BACKUP_DIR"/memory-* 2>/dev/null | tail -n +$((ROTATE_COUNT + 1)) | wc -l)
    if [ "$ROTATE_DELETED" -gt 0 ]; then
        ls -1dt "$BACKUP_DIR"/memory-* 2>/dev/null | tail -n +$((ROTATE_COUNT + 1)) | xargs -r rm -rf
        echo "[day-close]   rotate=OK — удалено $ROTATE_DELETED старых бэкапа (храним $ROTATE_COUNT)"
    else
        echo "[day-close]   rotate=OK — бэкапов ≤$ROTATE_COUNT, удалять нечего"
    fi
else
    echo "[day-close]   backup=SKIP — $MEMORY_DIR не найден"
fi

echo "[day-close] Шаг 2/3: Knowledge-MCP reindex"
REINDEX_SCRIPT="$WORKSPACE_DIR/DS-MCP/knowledge-mcp/scripts/selective-reindex.sh"
if [ -f "$REINDEX_SCRIPT" ]; then
    bash "$REINDEX_SCRIPT"
    echo "[day-close]   reindex=OK"
else
    echo "[day-close]   reindex=SKIP — $REINDEX_SCRIPT не найден"
fi

echo "[day-close] Шаг 3/3: Linear sync"
LINEAR_SCRIPT="$DS_STRATEGY/scripts/linear-sync.sh"
if [ -f "$LINEAR_SCRIPT" ]; then
    bash "$LINEAR_SCRIPT"
    echo "[day-close]   linear=OK"
else
    echo "[day-close]   linear=SKIP — $LINEAR_SCRIPT не найден"
fi

echo "[day-close] === Готово ==="
