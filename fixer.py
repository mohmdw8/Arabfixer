"""
fixer.py – وحدة التصحيح الأساسية
المرحلتان: لحام الحروف (Reshaping) + ضبط الاتجاه (BiDi)
"""

import arabic_reshaper
from bidi.algorithm import get_display
import re


def fix_text(text: str) -> str:
    """
    التصحيح الكامل لنص عربي:
    1. لحام الحروف المتفرقة (arabic_reshaper)
    2. ضبط اتجاه العرض من اليمين لليسار (python-bidi)
    النتيجة: نص يظهر صحيحاً في الطرفيات التي لا تدعم العربية.
    """
    if not text or not text.strip():
        return text

    lines = text.splitlines()
    fixed_lines = []

    for line in lines:
        if not line.strip():
            fixed_lines.append(line)
            continue
        # المرحلة 1: لحام الحروف
        reshaped = arabic_reshaper.reshape(line)
        # المرحلة 2: ضبط الاتجاه (يعكس ما يلزم عكسه تلقائياً)
        fixed = get_display(reshaped)
        fixed_lines.append(fixed)

    return "\n".join(fixed_lines)


def contains_arabic(text: str) -> bool:
    """كشف إن كان النص يحتوي على حروف عربية."""
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    return bool(arabic_pattern.search(text))
