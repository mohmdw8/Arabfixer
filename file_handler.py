import os
import json
import csv
import re
from pathlib import Path
from fixer import fix_text
from translator import translate_and_fix, translate_lines

# أنواع الملفات النصية البسيطة
TEXT_EXTENSIONS = {".txt", ".md", ".rst", ".log", ".html", ".xml", ".yaml", ".yml", ".ini", ".cfg", ".toml"}

# أنواع الملفات الهيكلية (تحتاج معالجة خاصة)
STRUCTURED_EXTENSIONS = {".py", ".js", ".ts", ".json", ".csv"}


# ──────────────────────────────────────────────
# معالجة ملف واحد بمساره الكامل (-f)
# ──────────────────────────────────────────────

def fix_file(filepath: str, translate: bool = False) -> str:
    """تصحيح (أو ترجمة+تصحيح) ملف واحد بمساره الكامل."""
    path = Path(filepath)

    if not path.exists():
        return f"❌ الملف غير موجود: {filepath}"

    ext = path.suffix.lower()

    if ext == ".json":
        return _process_json(path, translate)
    elif ext == ".csv":
        return _process_csv(path, translate)
    elif ext in STRUCTURED_EXTENSIONS:
        return _process_code_file(path, translate)
    else:
        return _process_text_file(path, translate)


def save_file(original_path: str, content: str, output_dir: str = None) -> str:
    """حفظ الملف المعالج في المجلد المحدد أو الافتراضي."""
    original = Path(original_path)

    if output_dir:
        out_dir = Path(output_dir)
    else:
        # المجلد الافتراضي
        script_dir = Path(__file__).parent
        out_dir = script_dir / "workspace"

    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / original.name

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    return str(output_path)


# ──────────────────────────────────────────────
# البحث عن الملفات والمجلدات بالاسم (-p)
# ──────────────────────────────────────────────

def find_and_fix_by_name(filename: str, translate: bool = False, search_root: str = None) -> dict:
    """البحث عن ملف بالاسم في النظام."""
    if search_root is None:
        if os.path.exists("/sdcard"):
            search_root = Path("/sdcard")
        else:
            search_root = Path.home()
    else:
        search_root = Path(search_root)

    matches = list(search_root.rglob(filename))

    if not matches:
        return {"status": "not_found", "results": []}

    if len(matches) == 1:
        content = fix_file(str(matches[0]), translate=translate)
        return {"status": "found", "results": [{"path": str(matches[0]), "content": content}]}

    return {"status": "multiple", "results": [{"path": str(m)} for m in matches]}


def find_directory_by_name(dir_name: str, search_root: str = None) -> dict:
    """البحث عن مجلد بالاسم في النظام."""
    if search_root is None:
        if os.path.exists("/sdcard"):
            search_root = Path("/sdcard")
        else:
            search_root = Path.home()
    else:
        search_root = Path(search_root)

    # البحث عن المجلدات المطابقة بالاسم
    matches = [p for p in search_root.rglob(dir_name) if p.is_dir()]

    if not matches:
        return {"status": "not_found", "results": []}

    if len(matches) == 1:
        return {"status": "found", "results": [{"path": str(matches[0])}]}

    return {"status": "multiple", "results": [{"path": str(m)} for m in matches]}


def fix_selected_file(path: str, translate: bool = False) -> dict:
    """تصحيح ملف بعد اختياره من القائمة."""
    content = fix_file(path, translate=translate)
    return {"path": path, "content": content}


# ──────────────────────────────────────────────
# معالجة مجلد كامل (-d / -dt)
# ──────────────────────────────────────────────

def process_directory(dirpath: str, translate: bool = False) -> list:
    """معالجة جميع الملفات داخل مجلد وإعادة قائمة مرتبة."""
    dir_path = Path(dirpath)

    if not dir_path.exists() or not dir_path.is_dir():
        return []

    results = []
    all_files = sorted([f for f in dir_path.iterdir() if f.is_file()])

    for file in all_files:
        content = fix_file(str(file), translate=translate)
        results.append({
            "name": file.name,
            "path": str(file),
            "content": content
        })

    return results


def save_selected_files(results: list, indices: list, output_dir: str = None) -> list:
    """حفظ ملفات محددة من النتائج."""
    saved = []
    for idx in indices:
        i = idx - 1
        if 0 <= i < len(results):
            item = results[i]
            saved_path = save_file(item["path"], item["content"], output_dir)
            saved.append(saved_path)
    return saved


def save_all_files(results: list, output_dir: str = None) -> list:
    """حفظ جميع الملفات."""
    indices = list(range(1, len(results) + 1))
    return save_selected_files(results, indices, output_dir)


# ──────────────────────────────────────────────
# دوال داخلية للمعالجة
# ──────────────────────────────────────────────

def _process_text_file(path: Path, translate: bool) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return f"❌ لا يمكن قراءة الملف (ترميز غير مدعوم): {path.name}"

    if translate:
        return translate_lines(content)
    else:
        return fix_text(content)


def _process_json(path: Path, translate: bool) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ خطأ في قراءة JSON: {e}"

    def process_value(val):
        if isinstance(val, str):
            return translate_and_fix(val) if translate else fix_text(val)
        elif isinstance(val, dict):
            return {k: process_value(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [process_value(i) for i in val]
        return val

    processed = process_value(data)
    return json.dumps(processed, ensure_ascii=False, indent=2)


def _process_csv(path: Path, translate: bool) -> str:
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception as e:
        return f"❌ خطأ في قراءة CSV: {e}"

    processed_rows = []
    for row in rows:
        new_row = []
        for cell in row:
            fixed_cell = translate_and_fix(cell) if translate else fix_text(cell)
            new_row.append(fixed_cell)
        processed_rows.append(new_row)

    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(processed_rows)
    return output.getvalue()


def _process_code_file(path: Path, translate: bool) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        return f"❌ لا يمكن قراءة الملف: {path.name}"

    def fix_match(m):
        original = m.group(0)
        inner = m.group(1)
        fixed = translate_and_fix(inner) if translate else fix_text(inner)
        return original.replace(inner, fixed)

    content = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', fix_match, content)
    content = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", fix_match, content)
    content = re.sub(r'(#\s*)([\u0600-\u06FF].*)', lambda m: m.group(1) + fix_text(m.group(2)), content)

    return content
