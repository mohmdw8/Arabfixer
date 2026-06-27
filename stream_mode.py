"""
stream_mode.py – وضع التدفق التلقائي
arb -s /مسار/الملف  → يشغّل الملف ويترجم كل مخرجاته تلقائياً
arb -s -p "اسم"     → يبحث عن الملف أولاً ثم يشغّله
"""

import os
import sys
import pty
import select
import subprocess
from pathlib import Path
from translator import translate_and_fix
from fixer import fix_text


def run_with_stream(filepath: str):
    """
    يشغّل الملف داخل طرفية وهمية (pty).
    كل سطر يطبعه الملف يُعترض، يُترجم، يُصحح، ثم يُعرض.
    """
    path = Path(filepath)

    if not path.exists():
        print(fix_text(f"❌ الملف غير موجود: {filepath}"))
        return

    # تحديد طريقة التشغيل حسب نوع الملف
    cmd = _build_command(path)
    if not cmd:
        print(fix_text(f"❌ نوع الملف غير مدعوم: {path.suffix}"))
        return

    print(fix_text(f"✓ جارٍ تشغيل: {path.name}"))
    print(fix_text("كل المخرجات ستُترجم وتُصحح تلقائياً"))
    print("─" * 40)

    # فتح pty واعتراض المخرجات
    master_fd, slave_fd = pty.openpty()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=slave_fd,
            stderr=slave_fd,
            stdin=slave_fd,
            close_fds=True
        )
        os.close(slave_fd)

        buffer = b""

        while True:
            # انتظار مخرجات من البرنامج
            try:
                rlist, _, _ = select.select([master_fd, sys.stdin], [], [], 0.1)
            except (ValueError, OSError):
                break

            # قراءة مخرجات البرنامج
            if master_fd in rlist:
                try:
                    data = os.read(master_fd, 1024)
                    if not data:
                        break
                    buffer += data

                    # معالجة سطراً سطراً
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        _process_and_print(line.decode("utf-8", errors="replace"))

                except OSError:
                    break

            # إرسال مدخلات المستخدم للبرنامج
            if sys.stdin in rlist:
                try:
                    user_input = os.read(sys.stdin.fileno(), 1024)
                    os.write(master_fd, user_input)
                except OSError:
                    break

            # إن انتهى البرنامج
            if process.poll() is not None:
                # طباعة ما تبقى في البفر
                if buffer:
                    _process_and_print(buffer.decode("utf-8", errors="replace"))
                break

    finally:
        try:
            os.close(master_fd)
        except OSError:
            pass

    print()
    print("─" * 40)
    print(fix_text("✓ انتهى تشغيل الملف."))


def _process_and_print(line: str):
    """
    معالجة سطر واحد من المخرجات:
    - إن كان أجنبياً: يُترجم ثم يُصحح
    - إن كان عربياً مكسوراً: يُصحح فقط
    - إن كان عربياً سليماً: يُعرض كما هو
    """
    from translator import has_foreign_words

    line = line.rstrip("\r\n")
    if not line.strip():
        print()
        return

    if has_foreign_words(line):
        # فيه أجنبي → ترجمة + تصحيح
        result = translate_and_fix(line)
    else:
        # عربي فقط → تصحيح فقط
        result = fix_text(line)

    print(result)


def _build_command(path: Path) -> list:
    """
    يبني أمر التشغيل المناسب حسب نوع الملف.
    """
    ext = path.suffix.lower()
    p = str(path)

    commands = {
        ".py":   [sys.executable, p],
        ".sh":   ["bash", p],
        ".js":   ["node", p],
        ".rb":   ["ruby", p],
        ".php":  ["php", p],
        ".pl":   ["perl", p],
        ".ts":   ["ts-node", p],
        ".r":    ["Rscript", p],
        "":      [p],  # ملف تنفيذي مباشر
    }

    return commands.get(ext, None)


def find_and_stream(filename: str):
    """
    يبحث عن الملف بالاسم ثم يشغّله بوضع التدفق.
    إن وُجد أكثر من ملف يطلب الاختيار.
    """
    from file_handler import find_and_fix_by_name
    from ui import show_multiple_files_choice

    # نبحث عن الملف (بدون تصحيح محتواه، فقط للحصول على مساره)
    result = find_and_fix_by_name(filename, translate=False)

    if result["status"] == "not_found":
        print(fix_text(f"❌ لم يُعثر على ملف باسم: {filename}"))
        return

    elif result["status"] == "found":
        filepath = result["results"][0]["path"]
        run_with_stream(filepath)

    elif result["status"] == "multiple":
        chosen_path = show_multiple_files_choice(result["results"])
        if chosen_path:
            run_with_stream(chosen_path)
