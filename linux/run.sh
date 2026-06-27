#!/bin/bash
# run.sh – تشغيل Arab Fixer مع بحث تلقائي عن arb.py

find_arb() {
    # 1) ملف .arb_path المحفوظ من setup
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local arb_dir
    arb_dir="$(dirname "$script_dir")"

    if [[ -f "$arb_dir/.arb_path" ]]; then
        local saved
        saved=$(cat "$arb_dir/.arb_path")
        if [[ -f "$saved" ]]; then
            echo "$saved"; return 0
        fi
    fi

    # 2) المجلد الأب مباشرة
    if [[ -f "$arb_dir/arb.py" ]]; then
        echo "$arb_dir/arb.py"; return 0
    fi

    # 3) which / command (لو كان مسجلاً في PATH)
    local by_which
    by_which=$(python3 -c "import arb" 2>/dev/null && python3 -c "import arb; print(arb.__file__)" 2>/dev/null)
    if [[ -n "$by_which" ]]; then
        echo "$by_which"; return 0
    fi

    # 4) بحث في HOME
    local found
    found=$(find "$HOME" -maxdepth 6 -name "arb.py" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"; return 0
    fi

    # 5) بحث عام
    found=$(find /opt /usr/local "$HOME" -maxdepth 8 -name "arb.py" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"; return 0
    fi

    return 1
}

ARB_PY=$(find_arb)
if [[ -z "$ARB_PY" ]]; then
    echo "❌ لم يتم العثور على arb.py"
    echo "   شغل linux/setup.sh أولاً."
    exit 1
fi

ARB_DIR=$(dirname "$(realpath "$ARB_PY")")

# الانتقال لمجلد المشروع ليجد الوحدات (fixer.py, ui.py...)
cd "$ARB_DIR" || exit 1

exec python3 "$ARB_PY" "$@"
