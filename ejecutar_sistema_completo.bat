@echo off
echo ====================================
echo   SISTEMA DE GESTION INTEGRAL
echo ====================================
echo.
echo Iniciando aplicaciones...
echo.
echo 📦 Gestion de Materiales: http://localhost:5000
echo 🔧 Control de Herramientas: http://localhost:5001
echo.
echo Presiona Ctrl+C para detener ambas aplicaciones
echo.

REM Ejecutar ambas aplicaciones en paralelo
start "Materiales" cmd /k "cd /d %~dp0 && python app.py"
timeout /t 2 /nobreak >nul
start "Herramientas" cmd /k "cd /d %~dp0 && python herramientas.py"

echo Aplicaciones iniciadas!
echo Puedes acceder desde cualquier navegador web.
pause