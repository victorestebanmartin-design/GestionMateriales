@echo off
chcp 65001 >nul
title Descarga Python Portable - Gestión de Materiales

echo.
echo =========================================================
echo   DESCARGA PYTHON PORTABLE - GESTIÓN DE MATERIALES
echo =========================================================
echo.
echo 🎯 Este script descarga Python Embebido para crear
echo    un paquete completamente portable (sin instalación)
echo.
echo ⚠️  REQUIERE:
echo    • Conexión a Internet (solo para descargar)
echo    • Se ejecuta SOLO UNA VEZ en el PC con internet
echo.
pause

echo.
echo 📋 PASO 1/3: Descargando Python Embebido...
echo 🌐 Descargando desde python.org...

:: Crear directorio para Python portable
if not exist "python_portable" mkdir python_portable

:: Descargar Python embebido (versión más reciente estable)
echo ⏳ Descargando python-3.13.0-embed-amd64.zip...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip' -OutFile 'python_portable\python-embed.zip'}"

if %errorlevel% neq 0 (
    echo ❌ Error descargando Python embebido
    echo 💡 Intente descargar manualmente desde:
    echo    https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip
    echo    Y guárdelo como: python_portable\python-embed.zip
    pause
    exit /b 1
)

echo ✅ Python embebido descargado

echo.
echo 📋 PASO 2/3: Extrayendo Python...
powershell -Command "Expand-Archive -Path 'python_portable\python-embed.zip' -DestinationPath 'python_portable\' -Force"

if %errorlevel% neq 0 (
    echo ❌ Error extrayendo Python
    pause
    exit /b 1
)

echo ✅ Python extraído

echo.
echo 📋 PASO 3/3: Descargando get-pip.py...
echo ⏳ Descargando instalador de pip...
powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'python_portable\get-pip.py'"

if %errorlevel% neq 0 (
    echo ❌ Error descargando get-pip.py
    echo 💡 Intente descargar manualmente desde:
    echo    https://bootstrap.pypa.io/get-pip.py
    echo    Y guárdelo en: python_portable\get-pip.py
    pause
    exit /b 1
)

echo ✅ get-pip.py descargado

echo.
echo 📋 Configurando Python embebido...

:: Habilitar pip en Python embebido
echo import site > python_portable\python313._pth
echo python313.zip >> python_portable\python313._pth
echo . >> python_portable\python313._pth
echo .\Scripts >> python_portable\python313._pth

echo ✅ Configuración completada

:: Limpiar archivo zip
del python_portable\python-embed.zip >nul 2>&1

echo.
echo =========================================================
echo   ✅ PYTHON PORTABLE PREPARADO
echo =========================================================
echo.
echo 📁 Ubicación: python_portable\
echo 🐍 Ejecutable: python_portable\python.exe
echo.
echo 🚀 Siguiente paso:
echo    • Ejecute: preparar_paquete_completo.bat
echo    • Esto instalará las dependencias en Python portable
echo.
echo 💾 Todo estará listo para copiar al PC sin internet
echo.
pause