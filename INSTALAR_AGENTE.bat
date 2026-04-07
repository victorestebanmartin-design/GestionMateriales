@echo off
title Instalar dependencias Agente Excel
echo.
echo ============================================================
echo   Instalando dependencias del Agente Bajas Excel
echo ============================================================
echo.
echo  Comprobando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo         Descargalo de https://www.python.org/downloads/
    echo         Marca "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)
python --version
echo.
echo  Instalando paquetes necesarios...
python -m pip install --upgrade pip
python -m pip install pywin32 requests
echo.
echo  Configurando pywin32...
python -m pywin32_postinstall -install 2>nul
echo.
echo ============================================================
echo   Listo. Ahora puedes ejecutar AGENTE_EXCEL.bat
echo ============================================================
pause
