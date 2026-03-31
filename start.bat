@echo off
:: Ir siempre a la carpeta donde esta este .bat
cd /d "%~dp0"
title Gestion de Materiales
call .venv\Scripts\activate.bat

:inicio
python run_app_window.py
:: Codigo 42 = reinicio solicitado desde el admin (actualizar app)
if %errorlevel% equ 42 (
    echo Reiniciando aplicacion...
    timeout /t 2 /nobreak >nul
    goto inicio
)
pause
