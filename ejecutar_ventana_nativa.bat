@echo off
title Gestión de Materiales - Modo Ventana
echo ================================================================
echo                    GESTIÓN DE MATERIALES
echo                      Modo Ventana Nativa
echo                       (Sin barra del navegador)
echo ================================================================
echo.
echo 🚀 Iniciando aplicación en ventana nativa...
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
    if errorlevel 1 (
        echo ERROR al instalar pywebview
        pause
        exit /b 1
    )
)

echo ✅ Dependencias verificadas
echo.
echo ================================================================
echo    La aplicacion se abrira MAXIMIZADA (sin barra del navegador)
echo.
echo    CONTROLES:
echo      - Boton X (arriba a la derecha): Cerrar aplicacion
echo      - Alt+F4: Cerrar aplicacion
echo      - F11: Activar/desactivar pantalla completa total
echo      - Boton minimizar: Minimizar ventana
echo ================================================================
echo.

:: Ejecutar la aplicación con ventana nativa
%PYTHON_EXE% run_app_window.py

echo.
echo 👋 Aplicación cerrada
pause
