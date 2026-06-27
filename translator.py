"""
translator.py – وحدة الترجمة وكشف اللغة
في وضع -t: يترجم النص كله إلى العربية بغض النظر عن لغته
ثم يُصحح النتيجة
"""

from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
from fixer import fix_text
import re


def detect_language(text: str) -> str:
    """كشف لغة النص تلقائياً."""
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def has_foreign_words(text: str) -> bool:
    """
    يكشف إن كان النص يحتوي على كلمات غير عربية (إنجليزية أو غيرها).
    يبحث عن أي حروف لاتينية في النص.
    """
    return bool(re.search(r'[a-zA-Z]', text))


def translate_to_arabic(text: str) -> str:
    """
    ترجمة النص كله إلى العربية.
    - إن كان النص عربياً فقط بدون أي كلمة أجنبية: يُعاد كما هو.
    - إن كان فيه أي كلمة أجنبية: يُترجم كله إلى العربية.
    """
    if not text or not text.strip():
        return text

    # إذا لا يوجد أي حرف أجنبي → عربي خالص → لا ترجمة
    if not has_foreign_words(text):
        return text

    try:
        translated = GoogleTranslator(source="auto", target="ar").translate(text)
        return translated if translated else text
    except Exception as e:
        print(f"خطأ في الترجمة: {e}")
        return text


def translate_and_fix(text: str) -> str:
    """
    الدالة الرئيسية لوضع الترجمة (-t):
    1. ترجمة النص كله إلى العربية (حتى لو مختلط)
    2. تصحيح النتيجة (لحام + ضبط اتجاه)
    """
    translated = translate_to_arabic(text)
    fixed = fix_text(translated)
    return fixed


def translate_lines(text: str) -> str:
    """
    ترجمة نص متعدد الأسطر سطراً سطراً.
    كل سطر يُترجم كله إلى العربية ثم يُصحح.
    """
    lines = text.splitlines()
    result = []

    for line in lines:
        if not line.strip():
            result.append(line)
            continue
        result.append(translate_and_fix(line))

    return "\n".join(result)
