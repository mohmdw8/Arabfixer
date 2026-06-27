@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo === إعداد Arab Fixer لـ Windows ===
echo.

REM ── البحث عن arb.py بدءاً من مجلد الـ setup ──
SET SETUP_DIR=%~dp0
SET ARB_PY=

REM المجلد الأب مباشرة (التوقع الافتراضي)
IF EXIST "%SETUP_DIR%..\arb.py" (
    SET ARB_PY=%SETUP_DIR%..\arb.py
    GOTO :FOUND
)

REM البحث في الأجداد حتى 3 مستويات
SET CHECK=%SETUP_DIR%..\..\arb.py
IF EXIST "%CHECK%" (SET ARB_PY=%CHECK%& GOTO :FOUND)

SET CHECK=%SETUP_DIR%..\..\..\arb.py
IF EXIST "%CHECK%" (SET ARB_PY=%CHECK%& GOTO :FOUND)

REM البحث في القرص بالكامل باستخدام where أو dir
echo البحث عن arb.py في القرص... (قد يستغرق لحظة)
FOR /F "delims=" %%F IN ('dir /s /b "%USERPROFILE%\arb.py" 2^>nul') DO (
    SET ARB_PY=%%F
    GOTO :FOUND
)
FOR /F "delims=" %%F IN ('dir /s /b "C:\arb.py" 2^>nul') DO (
    SET ARB_PY=%%F
    GOTO :FOUND
)

echo ❌ لم يتم العثور على arb.py - تأكد أن الملفات موجودة.
pause
exit /b 1

:FOUND
REM تحويل المسار لمطلق
FOR %%F IN ("%ARB_PY%") DO SET ARB_PY=%%~fF
SET ARB_DIR=%ARB_PY%\..
FOR %%D IN ("%ARB_DIR%") DO SET ARB_DIR=%%~fD

echo ✓ تم العثور على arb.py في: %ARB_PY%
echo.

REM ── تثبيت المتطلبات ──
IF EXIST "%ARB_DIR%\requirements.txt" (
    echo تثبيت المتطلبات...
    pip install -r "%ARB_DIR%\requirements.txt"
) ELSE (
    echo تخطي requirements.txt - الملف غير موجود.
)

REM ── إنشاء arb.bat في مجلد المشروع ──
SET ARB_BAT=%ARB_DIR%\arb.bat
echo @echo off > "%ARB_BAT%"
echo python "%ARB_PY%" %%* >> "%ARB_BAT%"
echo ✓ تم إنشاء %ARB_BAT%

REM ── إضافة مجلد المشروع إلى PATH ──
echo.
echo هل تريد إضافة المجلد إلى PATH حتى تكتب arb من أي مكان؟ (y/n)
set /p ADDPATH=
IF /I "%ADDPATH%"=="y" (
    REM إضافة للمستخدم الحالي دون صلاحية Admin
    FOR /F "skip=2 tokens=3*" %%A IN ('reg query "HKCU\Environment" /v PATH 2^>nul') DO SET CUR_PATH=%%A %%B
    echo !CUR_PATH! | find /i "%ARB_DIR%" >nul 2>&1
    IF ERRORLEVEL 1 (
        setx PATH "!CUR_PATH!;%ARB_DIR%" >nul
        echo ✓ تمت الإضافة. أعد فتح الطرفية لتفعيل التغيير.
    ) ELSE (
        echo ✓ المجلد موجود في PATH بالفعل.
    )
)

echo.
echo === تم الإعداد! ===
echo لتشغيل الأداة: arb  (بعد إعادة فتح الطرفية)
echo أو: cd /d "%ARB_DIR%" ثم python arb.py
pause
