@echo off
title Agente Bajas Excel
echo.
echo ============================================================
echo   Agente Bajas Excel
echo ============================================================
echo.

REM ── Buscar Python ─────────────────────────────────────────
set PYTHON=
python --version >nul 2>&1
if not errorlevel 1 set PYTHON=python

if "%PYTHON%"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set PYTHON=py
)

if "%PYTHON%"=="" (
    echo  [ERROR] Python no encontrado.
    echo  Ejecuta primero INSTALAR_AGENTE.bat para instalarlo.
    pause
    exit /b 1
)

echo  Python encontrado:
%PYTHON% --version
echo.

REM ── Verificar pywin32 (necesario para automatizar Excel) ──
%PYTHON% -c "import win32com.client" >nul 2>&1
if errorlevel 1 (
    echo  [AVISO] Instalando pywin32...
    %PYTHON% -m pip install --quiet pywin32
    %PYTHON% -m pywin32_postinstall -install >nul 2>&1
    echo  pywin32 instalado.
    echo.
)

REM ── Obtener ruta completa del ejecutable Python ───────────
for /f "tokens=*" %%i in ('%PYTHON% -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i

echo  Iniciando agente (HTTP via PowerShell, Excel via Python)...
echo  (Pulsa Ctrl+C para detener)
echo.

REM ── Lanzar PS1 con ExecutionPolicy Bypass (no requiere admin) ──
REM    PowerShell hace las llamadas HTTP al servidor.
REM    Python solo automatiza Excel localmente (sin red).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0agente_excel.ps1" -PythonPath "%PYTHON_PATH%" %*

echo.
echo  El agente se ha detenido.
pause
