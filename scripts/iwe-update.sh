#!/usr/bin/env bash
# iwe-update.sh — wrapper для FMT-exocortex-template/update.sh
# Автоматически применяет локальные патчи до и после обновления шаблона.
#
# Usage: bash scripts/iwe-update.sh [--check|--yes]

set -euo pipefail

IWE_ROOT="${IWE_ROOT:-$HOME/IWE}"
IWE_TEMPLATE="${IWE_TEMPLATE:-$IWE_ROOT/FMT-exocortex-template}"
PATCH_FILE="$IWE_ROOT/memory/audit-fixes-linux-submodule.patch"

apply_patch() {
    local target_dir="$1"
    if [ ! -f "$PATCH_FILE" ]; then
        return 0
    fi
    if patch -N -p1 -d "$target_dir" --dry-run < "$PATCH_FILE" >/dev/null 2>&1; then
        patch -N -p1 -d "$target_dir" < "$PATCH_FILE"
        echo "✅ Patches applied to $(basename "$target_dir")"
    else
        echo "ℹ️  Patches already applied or no longer needed for $(basename "$target_dir")"
    fi
}

# Step 0: pre-apply patches to template (so update.sh copies fixed files into workspace)
if [ -f "$PATCH_FILE" ]; then
    echo "========================================"
    echo "  Pre-applying local patches to template"
    echo "========================================"
    apply_patch "$IWE_TEMPLATE"
fi

# Step 1: run upstream update.sh
echo ""
echo "========================================"
echo "  Running upstream update.sh"
echo "========================================"
bash "$IWE_TEMPLATE/update.sh" "$@"
UPDATE_EXIT=$?

if [ $UPDATE_EXIT -ne 0 ]; then
    echo ""
    echo "update.sh failed (exit $UPDATE_EXIT). Skipping post-patch."
    exit $UPDATE_EXIT
fi

# Step 2: re-apply patches to template (in case update.sh reverted them during self-update)
echo ""
echo "========================================"
echo "  Re-applying local patches (post-update)"
echo "========================================"
apply_patch "$IWE_TEMPLATE"

echo ""
echo "========================================"
echo "  Update complete"
echo "========================================"
