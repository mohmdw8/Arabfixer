#!/bin/bash
# setup.sh – إعداد Arab Fixer على Termux مع بحث تلقائي

echo "=== إعداد Arab Fixer لـ Termux ==="
echo

find_arb() {
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local candidates=(
        "$(dirname "$script_dir")/arb.py"
        "$HOME/arab_fixer/arb.py"
        "$HOME/arb.py"
        "/sdcard/arab_fixer/arb.py"
        "/storage/emulated/0/arab_fixer/arb.py"
    )

    for c in "${candidates[@]}"; do
        if [[ -f "$c" ]]; then
            realpath "$c" 2>/dev/null || echo "$c"
            return 0
        fi
    done

    # بحث في HOME و sdcard
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
    echo "   تأكد من نقل ملفات المشروع إلى الجهاز وأعد التشغيل."
    exit 1
fi

ARB_DIR=$(dirname "$ARB_PY")
echo "✓ تم العثور على arb.py في: $ARB_PY"
echo

# طلب صلاحية التخزين (مرة واحدة فقط)
if [[ ! -d "$HOME/storage" ]]; then
    echo "طلب صلاحية التخزين..."
    termux-setup-storage
    sleep 2
fi

# تحديث وتثبيت Python إن لزم
pkg install python -y -q

if [[ -f "$ARB_DIR/requirements.txt" ]]; then
    echo "تثبيت المتطلبات..."
    pip install -r "$ARB_DIR/requirements.txt" --quiet
fi

# إنشاء wrapper في $PREFIX/bin
ARB_LINK="$PREFIX/bin/arb"
cat > "$ARB_LINK" << WRAPPER
#!/bin/bash
cd "$ARB_DIR"
exec python "$ARB_PY" "\$@"
WRAPPER
chmod +x "$ARB_LINK"
echo "✓ تم إنشاء الاختصار: arb"

# حفظ المسار
echo "$ARB_PY" > "$ARB_DIR/.arb_path"

echo
echo "=== تم الإعداد! ==="
echo "الآن اكتب: arb  في أي مجلد"
