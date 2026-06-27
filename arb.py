import sys
import os
import json
import re
from pathlib import Path

# ── تأكد أن مجلد المشروع في sys.path دائماً ──
# هذا يحل مشكلة "ModuleNotFoundError" عند تشغيل arb.py من أي مكان
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

CONFIG_PATH = SCRIPT_DIR / "config.json"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_config(data: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _print_fixed(text: str):
    from fixer import fix_text
    print(fix_text(text))


# ──────────────────────────────────────────────
# محلل الأوامر الذكي والمدمج
# ──────────────────────────────────────────────

def parse_arguments(args: list) -> dict:
    """تحليل دقيق لمدخلات سطر الأوامر لتفكيك الاختصارات والأرقام ومواقع الحفظ."""
    parsed = {
        "mode": "text",         # text, file, directory, stream, self-repair, font
        "translate": False,
        "search": False,
        "indices": [],          # الأرقام المكتوبة كـ 4 أو 4,6,1
        "target": None,         # اسم الملف، المجلد، أو النص
        "save": False,          # هل يوجد حرف o
        "save_indices": [],    # أرقام الحفظ مثل o3,2
        "save_path": None,      # مسار الحفظ المحدد بعد o
        "font_name": None
    }

    if not args:
        return parsed

    # الأوامر المباشرة والخاصة
    if "-l" in args:
        parsed["mode"] = "self-repair"
        return parsed
    
    if "--f" in args:
        parsed["mode"] = "font"
        try:
            idx = args.index("--f")
            parsed["font_name"] = args[idx + 1]
        except IndexError:
            pass
        return parsed

    if "-s" in args:
        parsed["mode"] = "stream"
        remaining = [a for a in args if a != "-s"]
        if "-p" in remaining:
            parsed["search"] = True
            remaining.remove("-p")
        if remaining:
            parsed["target"] = remaining[0]
        return parsed

    # البحث عن أعلام الأوامر (مثل -f, -d, -dp, -ftp...)
    flags_arg = None
    for arg in args:
        if arg.startswith("-") and not arg.startswith("--"):
            flags_arg = arg
            break

    if flags_arg:
        flags = flags_arg.lstrip("-")
        if "f" in flags:
            parsed["mode"] = "file"
        elif "d" in flags:
            parsed["mode"] = "directory"
        
        if "t" in flags:
            parsed["translate"] = True
        if "p" in flags:
            parsed["search"] = True

    # البحث عن علم الحفظ 'o' أو 'o3,2'
    save_arg_idx = -1
    for i, arg in enumerate(args):
        if arg == "o" or re.match(r'^o\d+(,\d+)*$', arg):
            save_arg_idx = i
            parsed["save"] = True
            if arg != "o":
                # استخراج الأرقام من o3,2
                idx_str = arg[1:]
                parsed["save_indices"] = [int(x) for x in idx_str.split(",")]
            break

    # تحديد مسار الحفظ المخصص بعد حرف o
    if save_arg_idx != -1 and save_arg_idx + 1 < len(args):
        next_arg = args[save_arg_idx + 1]
        # التأكد من أنه ليس رمزاً أو رقماً عادياً
        if not next_arg.startswith("-") and not re.match(r'^\d+(,\d+)*$', next_arg) and next_arg != "o":
            parsed["save_path"] = next_arg

    # تحديد أرقام الملفات المطلوبة مثل 4 أو 4,6,1
    for arg in args:
        if re.match(r'^\d+(,\d+)*$', arg):
            parsed["indices"] = [int(x) for x in arg.split(",")]
            break

    # تحديد الهدف الرئيسي (النص أو المسار)
    for arg in args:
        if arg.startswith("-"):
            continue
        if re.match(r'^\d+(,\d+)*$', arg):
            continue
        if arg == "o" or re.match(r'^o\d+(,\d+)*$', arg):
            continue
        if parsed["save_path"] and arg == parsed["save_path"]:
            continue
        # هذا هو الهدف المتبقي
        parsed["target"] = arg
        break

    return parsed


# ──────────────────────────────────────────────
# معالجات المسارات الذكية والتشغيل
# ──────────────────────────────────────────────

def _handle_file_logic(parsed: dict):
    from file_handler import fix_file, save_file, find_and_fix_by_name
    from ui import show_multiple_files_choice

    filepath = parsed["target"]
    if not filepath:
        _print_fixed("❌ يرجى تحديد مسار أو اسم الملف.")
        return

    if parsed["search"]:
        res = find_and_fix_by_name(filepath, translate=parsed["translate"])
        if res["status"] == "not_found":
            _print_fixed(f"❌ لم يُعثر على ملف باسم: {filepath}")
            return
        elif res["status"] == "found":
            filepath = res["results"][0]["path"]
        elif res["status"] == "multiple":
            filepath = show_multiple_files_choice(res["results"])
            if not filepath:
                return

    content = fix_file(filepath, translate=parsed["translate"])

    if parsed["save"]:
        p = save_file(filepath, content, parsed["save_path"])
        _print_fixed(f"✓ تم الحفظ: {p}")
    else:
        print(content)


def _handle_directory_logic(parsed: dict):
    from file_handler import process_directory, save_file, find_directory_by_name
    from ui import show_directory_results, show_multiple_files_choice

    dirpath = parsed["target"]
    if not dirpath:
        _print_fixed("❌ يرجى تحديد مسار أو اسم المجلد.")
        return

    if parsed["search"]:
        res = find_directory_by_name(dirpath)
        if res["status"] == "not_found":
            _print_fixed(f"❌ لم يُعثر على مجلد باسم: {dirpath}")
            return
        elif res["status"] == "found":
            dirpath = res["results"][0]["path"]
        elif res["status"] == "multiple":
            # إعادة استخدام اختيار المجلدات المتعددة
            dirpath = show_multiple_files_choice(res["results"])
            if not dirpath:
                return

    results = process_directory(dirpath, translate=parsed["translate"])
    if not results:
        _print_fixed("❌ المجلد فارغ أو غير موجود.")
        return

    # الفلترة بالأرقام المحددة (مثال 4 أو 4,6,1)
    if parsed["indices"]:
        filtered_results = []
        for idx in parsed["indices"]:
            i = idx - 1
            if 0 <= i < len(results):
                filtered_results.append(results[i])
        results_to_use = filtered_results
    else:
        results_to_use = results

    # معالجة الحفظ (o)
    if parsed["save"]:
        # إذا حدد أرقاماً وراء o مثل o3,2
        indices_to_save = parsed["save_indices"] if parsed["save_indices"] else list(range(1, len(results_to_use) + 1))
        for idx in indices_to_save:
            i = idx - 1
            if 0 <= i < len(results_to_use):
                item = results_to_use[i]
                p = save_file(item["path"], item["content"], parsed["save_path"])
                _print_fixed(f"✓ تم الحفظ: {p}")
        return

    # عرض الملفات المحددة مباشرة على الطرفية إن لم يُطلب الحفظ
    if parsed["indices"]:
        for item in results_to_use:
            print(f"\n── {item['name']} ──")
            print(item["content"])
        return

    # الدخول للواجهة التفاعلية الافتراضية
    show_directory_results(results)


def main():
    args = sys.argv[1:]

    if not args:
        from ui import show_main_ui, handle_main_choice
        choice = show_main_ui()
        handle_main_choice(choice)
        return

    parsed = parse_arguments(args)

    if parsed["mode"] == "self-repair":
        _print_fixed("جارٍ إعادة تصحيح نصوص الواجهة...")
        config = load_config()
        save_config(config)
        _print_fixed("✓ تمت الصيانة الذاتية بنجاح.")
        return

    if parsed["mode"] == "font":
        if parsed["font_name"]:
            font_path = SCRIPT_DIR / "fonts" / parsed["font_name"]
            if not font_path.exists():
                _print_fixed(f"❌ الخط غير موجود في مجلد fonts/: {parsed['font_name']}")
                return
            config = load_config()
            config["font"] = parsed["font_name"]
            save_config(config)
            _print_fixed(f"✓ تم تعيين الخط: {parsed['font_name']}")
        else:
            _print_fixed("❌ يرجى تحديد اسم الخط.")
        return

    if parsed["mode"] == "stream":
        from ui import show_multiple_files_choice
        target = parsed["target"]
        if not target:
            _print_fixed("❌ يرجى تحديد ملف للتشغيل.")
            return
        
        filepath = target
        if parsed["search"]:
            from file_handler import find_and_fix_by_name
            res = find_and_fix_by_name(target, translate=False)
            if res["status"] == "not_found":
                _print_fixed(f"❌ لم يُعثر على ملف باسم: {target}")
                return
            elif res["status"] == "found":
                filepath = res["results"][0]["path"]
            elif res["status"] == "multiple":
                filepath = show_multiple_files_choice(res["results"])
                if not filepath:
                    return

        from stream_mode import run_with_stream
        run_with_stream(filepath)
        return

    if parsed["mode"] == "file":
        _handle_file_logic(parsed)
        return

    if parsed["mode"] == "directory":
        _handle_directory_logic(parsed)
        return

    # معالجة النصوص المباشرة
    if parsed["mode"] == "text" and parsed["target"]:
        if parsed["translate"]:
            from translator import translate_and_fix
            print(translate_and_fix(parsed["target"]))
        else:
            from fixer import fix_text
            print(fix_text(parsed["target"]))
        return

    _print_fixed("❌ أمر غير معروف. شغل الأداة دون أوامر لعرض التعليمات.")


if __name__ == "__main__":
    main()
