@echo off
title Agente Bajas Excel
echo.
echo ============================================================
echo   Agente Bajas Excel
echo ============================================================
echo.

REM Buscar Python
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

REM Verificar pywin32
%PYTHON% -c "import win32com.client" >nul 2>&1
if errorlevel 1 (
    echo  [AVISO] Instalando pywin32...
    %PYTHON% -m pip install --quiet pywin32
    %PYTHON% -m pywin32_postinstall -install >nul 2>&1
    echo  pywin32 instalado.
    echo.
)

echo  Iniciando agente local en localhost:8765...
echo  Abre el admin panel en el navegador y usa "Procesar en este PC".
echo  (Pulsa Ctrl+C para detener)
echo.
%PYTHON% "%~dp0baja_excel_agente.py" %*

echo.
echo  El agente se ha detenido.
pause
