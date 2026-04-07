@echo off
cd /d "%~dp0"
title Bajas Excel - Gestion de Materiales
color 0A

echo.
echo ============================================================
echo     BAJAS EXCEL - Procesar bajas en el Excel compartido
echo ============================================================
echo.
echo  ANTES DE CONTINUAR:
echo    1. Abre el Excel compartido (con las macros habilitadas)
echo    2. Ten el Excel visible en pantalla
echo.

:: Modo de ejecucion
set MODO=
if "%1"=="--lista" set MODO=--lista
if "%1"=="--uno"   set MODO=--uno
if "%1"=="--semi"  set MODO=--semi

if "%MODO%"=="--lista" (
    echo [MODO] Solo listado ^(sin procesar^)
    echo.
)
if "%MODO%"=="--uno" (
    echo [MODO] Automatico con confirmacion por cada baja
    echo.
)
if "%MODO%"=="--semi" (
    echo [MODO] Semi-automatico: el codigo se copia al portapapeles,
    echo        tu pegas con Ctrl+V y haces los clics manualmente.
    echo.
)
if "%MODO%"=="" (
    echo  Elige modo:
    echo    1. Semi-automatico  ^(recomendado^) - copies codigo, tu haces los clics
    echo    2. Automatico       - el script hace todo solo
    echo    3. Solo listado     - ver pendientes sin procesar
    echo    4. Salir
    echo.
    choice /C 1234 /M "Elige opcion"
    if errorlevel 4 exit /b 0
    if errorlevel 3 set MODO=--lista
    if errorlevel 2 (
        set MODO=
        echo.
        choice /C SN /M "¿Continuar en modo automatico?"
        if errorlevel 2 (
            echo Cancelado.
            pause
            exit /b 0
        )
    )
    if errorlevel 1 (
        if "%MODO%"=="" set MODO=--semi
    )
)

echo.
.venv\Scripts\python.exe baja_excel.py %MODO%

echo.
pause
