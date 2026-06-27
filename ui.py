import os
import sys
from fixer import fix_text

def fix(text: str) -> str:
    return fix_text(text)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ──────────────────────────────────────────────
# نصوص الواجهة
# ──────────────────────────────────────────────

def show_main_ui():
    clear_screen()
    sep = "─" * 55

    print()
    print("Arab Fixer – " + fix("مُصحح النصوص ومُترجم الأوامر في الطرفية"))
    print(fix("الإصدار 2.0 | نظام ذكي ومتكامل"))
    print(sep)
    print()

    print(fix("💡 الاختصارات والخيارات الأساسية (اكتبها مباشرة):"))
    print()

    shortcuts = [
        ('arb "نص"',             'تصحيح وعكس النص العربي مباشرة.'),
        ('arb -t "نص"',          'ترجمة النص إلى العربية وتصحيحه تلقائياً.'),
        ('arb -f "ملف.txt"',     'تصحيح وعكس نصوص الملف دون ترجمة.'),
        ('arb -ft "ملف.txt"',    'ترجمة كامل نصوص الملف وتصحيحها.'),
        ('arb -d "مجلد"',        'فتح مجلد وعرض ملفاته تفاعلياً لتصحيحها.'),
        ('arb -dt "مجلد"',       'معالجة مجلد بالكامل مع ترجمة ملفاته.'),
        ('arb -dp "مجلد"',       'البحث عن مجلد بجهازك ومعالجته (دون مسار كامل).'),
        ('arb -dtp "مجلد"',      'البحث عن مجلد، وترجمة جميع ملفاته وتصحيحها.'),
        ('arb -s "سكربت.py"',    'تشغيل البرامج وترجمة مخرجاتها لحظياً (Live).'),
    ]

    for cmd, desc in shortcuts:
        print(f"  {cmd:20s} ➔ {fix(desc)}")

    print()
    print(fix("⚙️ ميزات التحكم المتقدم والسريع بالأرقام والحفظ:"))
    print()
    advanced = [
        ('arb -d 4,6 "مجلد"',          'تصحيح وعرض الملفين 4 و 6 فقط من المجلد.'),
        ('arb -f "ملف.txt" o',         'تصحيح الملف وحفظه فوراً في مجلد الـ workspace.'),
        ('arb -d "مجلد" o',            'تصحيح وحفظ جميع ملفات المجلد تلقائياً.'),
        ('arb -dt "مجلد" o3,2 "مسار"', 'ترجمة وحفظ الملفين 3 و 2 فقط في مسار مخصص.'),
        ('arb -l',                     'إعادة الصيانة الذاتية وإصلاح نصوص الواجهة.'),
        ('arb --f "خط.ttf"',           'تغيير خط العرض المستخدم في النظام.'),
    ]

    for cmd, desc in advanced:
        print(f"  {cmd:28s} ➔ {fix(desc)}")

    print(sep)
    print()
    print(fix("اختر بيئة العمل:"))
    print()
    print("  1 – " + fix("العمل داخل") + " workspace/ " + fix("(الساندبوكس)"))
    print()

    try:
        choice = input(fix("اكتب 1 للدخول أو اضغط Enter للتخطي: ")).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        print(fix("مع السلامة!"))
        sys.exit(0)

    return choice


def handle_main_choice(choice: str):
    if choice == "1":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        workspace = os.path.join(script_dir, "workspace")
        os.makedirs(workspace, exist_ok=True)
        print()
        print(fix("✓ جارٍ العمل داخل") + " workspace/")
        print(fix(f"المسار: {workspace}"))
        os.chdir(workspace)


# ──────────────────────────────────────────────
# عرض نتائج المجلد (-d / -dt)
# ──────────────────────────────────────────────

def show_directory_results(results: list):
    if not results:
        print(fix("❌ لا توجد ملفات في المجلد."))
        return

    from file_handler import save_selected_files, save_all_files

    print()
    print(fix("الملفات المعالجة:"))
    print("─" * 40)

    for i, item in enumerate(results, start=1):
        print(f"  {i}. {item['name']}")

    print()
    print(fix("الأوامر المتاحة:"))
    print(fix("  رقم      ➔ عرض محتوى الملف"))
    print(fix("  o        ➔ حفظ جميع الملفات"))
    print(fix("  o7       ➔ حفظ ملف رقم 7"))
    print(fix("  o7,9,4   ➔ حفظ ملفات 7 و9 و4"))
    print(fix("  q        ➔ خروج"))
    print()

    while True:
        try:
            cmd = input(">>> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if cmd in ("q", ""):
            break

        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(results):
                print()
                print(f"── {results[idx]['name']} ──")
                print(results[idx]["content"])
                print()
            else:
                print(fix("❌ رقم خارج النطاق."))

        elif cmd.startswith("o"):
            suffix = cmd[1:].strip()
            output_dir = None

            parts = suffix.split(None, 1)
            index_part = parts[0] if parts else ""
            if len(parts) > 1 and not parts[1].replace(",", "").isdigit():
                output_dir = parts[1].strip()
                index_part = parts[0]

            if index_part == "" or index_part == "o":
                saved = save_all_files(results, output_dir)
                for p in saved:
                    print(fix(f"✓ تم الحفظ: {p}"))
            elif "," in index_part:
                try:
                    indices = [int(x.strip()) for x in index_part.split(",")]
                    saved = save_selected_files(results, indices, output_dir)
                    for p in saved:
                        print(fix(f"✓ تم الحفظ: {p}"))
                except ValueError:
                    print(fix("❌ صيغة غير صحيحة. مثال: o7,9,4"))
            elif index_part.isdigit():
                saved = save_selected_files(results, [int(index_part)], output_dir)
                for p in saved:
                    print(fix(f"✓ تم الحفظ: {p}"))
            else:
                print(fix("❌ صيغة غير معروفة."))

        else:
            print(fix("❌ أمر غير معروف."))


# ──────────────────────────────────────────────
# اختيار عند وجود ملفات متعددة بنفس الاسم (-p)
# ──────────────────────────────────────────────

def show_multiple_files_choice(matches: list) -> str:
    print()
    print(fix("وُجد أكثر من اختيار بهذا الاسم. اختر أحدها:"))
    print()

    for i, item in enumerate(matches, start=1):
        print(f"  {i}. {item['path']}")

    print()
    while True:
        try:
            choice = input(">>> ").strip()
        except (KeyboardInterrupt, EOFError):
            return None

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(matches):
                return matches[idx]["path"]

        print(fix("❌ اختيار غير صالح."))
