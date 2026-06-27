#!/bin/bash
# setup.sh – إعداد Arab Fixer على Linux مع بحث تلقائي عن arb.py

echo "=== إعداد Arab Fixer لـ Linux ==="
echo

# ── البحث الذكي عن arb.py ──
find_arb() {
    local candidates=(
        "$(dirname "$(realpath "${BASH_SOURCE[0]}")")/../arb.py"   # المجلد الأب
        "$(dirname "$(realpath "${BASH_SOURCE[0]}")")/../../arb.py" # جد
        "$HOME/arab_fixer/arb.py"
        "$HOME/arb.py"
    )

    for c in "${candidates[@]}"; do
        if [[ -f "$c" ]]; then
            realpath "$c"
            return 0
        fi
    done

    # بحث شامل في HOME
    local found
    found=$(find "$HOME" -maxdepth 6 -name "arb.py" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"
        return 0
    fi

    # بحث في /opt و /usr/local
    found=$(find /opt /usr/local -maxdepth 6 -name "arb.py" 2>/dev/null | head -1)
    if [[ -n "$found" ]]; then
        echo "$found"
        return 0
    fi

    return 1
}

ARB_PY=$(find_arb)
if [[ -z "$ARB_PY" ]]; then
    echo "❌ لم يتم العثور على arb.py"
    echo "   تأكد أن ملفات المشروع موجودة وأعد التشغيل."
    exit 1
fi

ARB_DIR=$(dirname "$ARB_PY")
echo "✓ تم العثور على arb.py في: $ARB_PY"
echo

# ── تثبيت المتطلبات ──
if [[ -f "$ARB_DIR/requirements.txt" ]]; then
    echo "تثبيت المتطلبات..."
    pip3 install -r "$ARB_DIR/requirements.txt" --quiet
fi

# ── إنشاء wrapper script في /usr/local/bin ──
ARB_LINK="/usr/local/bin/arb"

WRAPPER="#!/bin/bash
cd \"$ARB_DIR\"
exec python3 \"$ARB_PY\" \"\$@\""

if [[ -w "/usr/local/bin" ]]; then
    echo "$WRAPPER" > "$ARB_LINK"
    chmod +x "$ARB_LINK"
    echo "✓ تم إنشاء الاختصار: $ARB_LINK"
else
    echo "$WRAPPER" | sudo tee "$ARB_LINK" > /dev/null
    sudo chmod +x "$ARB_LINK"
    echo "✓ تم إنشاء الاختصار: $ARB_LINK (بصلاحيات sudo)"
fi

# ── حفظ المسار في config لاستخدامه في run.sh ──
echo "$ARB_PY" > "$ARB_DIR/.arb_path"

echo
echo "=== تم الإعداد! ==="
echo "الآن يمكنك كتابة: arb  من أي مكان"
