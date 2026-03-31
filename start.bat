@echo off
:: Ir siempre a la carpeta donde esta este .bat
cd /d "%~dp0"
title Gestion de Materiales
call .venv\Scripts\activate.bat
python run_app_window.py
pause
