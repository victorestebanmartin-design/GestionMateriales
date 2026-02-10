@echo off
chcp 65001 >nul
title Instalar python-barcode y pillow

echo ================================================================
echo   INSTALACIÓN DE CÓDIGOS DE BARRAS (python-barcode + pillow)
echo ================================================================
echo.
echo 📦 Instalando desde offline_packages_new...
echo.

REM ⚠️ EDITA ESTA LÍNEA con la ruta de Python del otro PC
REM Ejemplos:
REM set PYTHON_PATH=python_portable\python.exe
REM set PYTHON_PATH=C:\Python313\python.exe
REM set PYTHON_PATH=py

set PYTHON_PATH=python\python.exe

echo 🐍 Verificando Python...
%PYTHON_PATH% --version
if errorlevel 1 (
    echo.
    echo ❌ ERROR: No se encontró Python
    echo    Edita línea 14 de este archivo con la ruta correcta
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Python detectado
echo.
echo 📥 Instalando python-barcode...
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new python_barcode-0.16.1-py3-none-any.whl

echo.
echo 📥 Instalando pillow (soporte para imágenes)...
%PYTHON_PATH% -m pip install --no-index --find-links=offline_packages_new pillow-12.0.0-cp313-cp313-win_amd64.whl

echo.
echo 🧪 Verificando instalación...
%PYTHON_PATH% -c "import barcode; from barcode.writer import ImageWriter; print('✅ Códigos de barras funcionando correctamente')"

if errorlevel 1 (
    echo.
    echo ❌ ERROR en la verificación
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ✅ Instalación completada correctamente!
echo ================================================================
echo.
echo 🚀 Ahora reinicia la aplicación y verás los códigos de barras
echo.
pause
