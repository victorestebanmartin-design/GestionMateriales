@echo off
title Gestión de Materiales - Ventana Sin Bordes
echo ================================================================
echo                    GESTIÓN DE MATERIALES
echo                      Ventana Sin Bordes
echo                    (Apariencia Moderna)
echo ================================================================
echo.
echo 🚀 Iniciando aplicación en ventana sin bordes...
echo.

:: Usar el entorno virtual del proyecto si existe
if exist ".venv\Scripts\python.exe" (
    set PYTHON_EXE=.venv\Scripts\python.exe
    set PIP_EXE=.venv\Scripts\pip.exe
    echo ✅ Usando entorno virtual del proyecto
) else (
    set PYTHON_EXE=python
    set PIP_EXE=pip
)

:: Verificar si Python está instalado
%PYTHON_EXE% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta disponible
    pause
    exit /b 1
)

echo ✅ Python encontrado

:: Verificar si pywebview está instalado
%PYTHON_EXE% -c "import webview" >nul 2>&1
if errorlevel 1 (
    echo.
    echo pywebview no esta instalado
    echo Instalando dependencias necesarias...
    echo.
    %PIP_EXE% install pywebview
)

echo ✅ Dependencias verificadas
echo.
echo ================================================================
echo 🖥️  La aplicación se abrirá sin bordes (apariencia moderna)
echo.
echo 📋 CONTROLES:
echo   - Arrastrar: Clic en cualquier parte de la ventana
echo   - Cerrar: Ctrl+W o cerrar esta consola
echo   - Redimensionar: Desde las esquinas
echo.
echo 🔑 ACCESO ADMINISTRADOR:
echo   Usuario: 999999
echo   Contraseña: (dejar en blanco)
echo.
echo ⚠️  Mantén esta ventana abierta mientras usas la aplicación
echo ================================================================
echo.

:: Ejecutar la aplicación sin bordes
%PYTHON_EXE% run_app_frameless.py

echo.
echo 👋 Aplicación cerrada
pause
