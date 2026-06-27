#!/bin/bash
# run.sh – تشغيل Arab Fixer على Termux مع بحث تلقائي

find_arb() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local arb_dir
    arb_dir="$(dirname "$script_dir")"

    # 1) ملف .arb_path المحفوظ من setup
    if [[ -f "$arb_dir/.arb_path" ]]; then
        local saved
        saved=$(cat "$arb_dir/.arb_path")
        if [[ -f "$saved" ]]; then
            echo "$saved"; return 0
        fi
    fi

    # 2) المجلد الأب
    if [[ -f "$arb_dir/arb.py" ]]; then
        echo "$arb_dir/arb.py"; return 0
    fi

    # 3) بحث في HOME و sdcard
    local found
    found=$(find "$HOME" /sdcard /storage/emulated/0 -maxdepth 6 -name "arb.py" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"; return 0
    fi

    return 1
}

ARB_PY=$(find_arb)
if [[ -z "$ARB_PY" ]]; then
    echo "❌ لم يتم العثور على arb.py"
    echo "   شغل termux/setup.sh أولاً."
    exit 1
fi

ARB_DIR=$(dirname "$ARB_PY")
cd "$ARB_DIR" || exit 1

exec python "$ARB_PY" "$@"
