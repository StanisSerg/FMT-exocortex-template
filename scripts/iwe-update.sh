#!/usr/bin/env bash
# iwe-update.sh — wrapper для FMT-exocortex-template/update.sh
# Автоматически применяет локальные патчи после обновления шаблона.
#
# Usage: bash scripts/iwe-update.sh [--check|--yes]

set -euo pipefail

IWE_ROOT="${IWE_ROOT:-$HOME/IWE}"
IWE_TEMPLATE="${IWE_TEMPLATE:-$IWE_ROOT/FMT-exocortex-template}"
PATCH_FILE="$IWE_ROOT/memory/audit-fixes-linux-submodule.patch"

# Step 1: run upstream update.sh
echo "========================================"
echo "  Running upstream update.sh"
echo "========================================"
bash "$IWE_TEMPLATE/update.sh" "$@"
UPDATE_EXIT=$?

if [ $UPDATE_EXIT -ne 0 ]; then
    echo ""
    echo "update.sh failed (exit $UPDATE_EXIT). Skipping patch application."
    exit $UPDATE_EXIT
fi

# Step 2: re-apply local patches (if patch file exists)
if [ -f "$PATCH_FILE" ]; then
    echo ""
    echo "========================================"
    echo "  Re-applying local patches"
    echo "========================================"
    echo "Patch: $PATCH_FILE"
    if patch -N -p1 -d "$IWE_TEMPLATE" --dry-run < "$PATCH_FILE" >/dev/null 2>&1; then
        patch -N -p1 -d "$IWE_TEMPLATE" < "$PATCH_FILE"
        echo "✅ Patches applied successfully."
    else
        echo "ℹ️  Patches already applied or no longer needed (dry-run failed)."
    fi
else
    echo ""
    echo "ℹ️  No local patch file found at $PATCH_FILE"
fi

echo ""
echo "========================================"
echo "  Update complete"
echo "========================================"
