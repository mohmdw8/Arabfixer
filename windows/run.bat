@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM ── أولاً: البحث عن arb.py بذكاء ──
SET ARB_PY=

REM 1) نفس مجلد run.bat (../arb.py)
SET CHECK=%~dp0..\arb.py
IF EXIST "%CHECK%" (
    FOR %%F IN ("%CHECK%") DO SET ARB_PY=%%~fF
    GOTO :RUN
)

REM 2) في PATH (لو سبق التثبيت)
FOR /F "delims=" %%F IN ('where arb.py 2^>nul') DO (
    SET ARB_PY=%%F
    GOTO :RUN
)

REM 3) بحث في مجلد المستخدم
FOR /F "delims=" %%F IN ('dir /s /b "%USERPROFILE%\arb.py" 2^>nul') DO (
    SET ARB_PY=%%F
    GOTO :RUN
)

REM 4) بحث في القرص C
FOR /F "delims=" %%F IN ('dir /s /b "C:\arb.py" 2^>nul') DO (
    SET ARB_PY=%%F
    GOTO :RUN
)

echo ❌ لم يتم العثور على arb.py
echo شغل setup.bat أولاً أو أضف مسار المجلد يدوياً.
pause
exit /b 1

:RUN
SET ARB_DIR=%ARB_PY%\..
FOR %%D IN ("%ARB_DIR%") DO SET ARB_DIR=%%~fD

REM الانتقال لمجلد المشروع ليجد الوحدات الأخرى (fixer.py, ui.py...)
cd /d "%ARB_DIR%"

python "%ARB_PY%" %*
