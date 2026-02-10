@echo off
chcp 65001 >nul
title Instalando dependencias en Python Portable

echo ================================================================
echo     INSTALACIÓN DE DEPENDENCIAS EN PYTHON PORTABLE
echo ================================================================
echo.
echo 📦 Instalando paquetes desde offline_packages_new...
echo.

REM Usar el Python portable de la carpeta python_portable
set PYTHON_PATH=python_portable\python.exe

echo 🐍 Verificando Python portable...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se encontró Python portable en python_portable\python.exe
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Python portable detectado
echo.
echo 📥 Instalando dependencias (esto puede tardar un minuto)...
echo.

REM Instalar cada paquete desde offline_packages_new
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new Flask
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new Werkzeug
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new openpyxl
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new python-barcode
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new pillow
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new blinker
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new click
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new itsdangerous
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new jinja2
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new markupsafe
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new colorama
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new et-xmlfile

echo.
echo ================================================================
echo ✅ Instalación completada!
echo ================================================================
echo.
echo 🚀 Ahora puedes ejecutar la aplicación con: INICIAR_APLICACION.bat
echo.
pause
