@echo off
title Gestión de Materiales
echo ================================================================
echo                    GESTIÓN DE MATERIALES
echo                   Versión Ejecutable Independiente v2.0
echo ================================================================
echo.
echo 🚀 Iniciando aplicación...
echo.

:: Verificar si el ejecutable existe
if not exist "GestionMateriales.exe" (
    echo ❌ ERROR: No se encontró GestionMateriales.exe
    echo Por favor verifica que todos los archivos estén presentes
    pause
    exit /b 1
)

echo ✅ Ejecutable encontrado
echo 🔧 Inicializando sistema...

:: Detectar IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "ip=%%a"
    goto :found
)
:found
set ip=%ip:~1%

echo.
echo 🌐 La aplicación se iniciará en tu navegador web automáticamente
echo.
echo 📡 Accesos disponibles:
echo   - Local: http://localhost:5000
if defined ip echo   - Red: http://%ip%:5000
echo.
echo 🔑 ACCESO ADMINISTRADOR:
echo   Usuario: 999999
echo   Contraseña: (dejar en blanco)
echo.
echo ⚠️  Para cerrar la aplicación: Presiona Ctrl+C en esta ventana
echo ================================================================
echo.

:: Ejecutar la aplicación
echo Abriendo navegador en 3 segundos...
timeout /t 3 /nobreak >nul
start "" http://localhost:5000
echo.
echo 🟢 Aplicación iniciada - Mantén esta ventana abierta
echo.
GestionMateriales.exe

echo.
echo 🔴 Aplicación cerrada
pause