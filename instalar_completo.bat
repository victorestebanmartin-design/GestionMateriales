@echo off
chcp 65001 >nul
title Instalación Completa - Gestión de Materiales

echo.
echo ========================================================
echo   INSTALACIÓN COMPLETA - GESTIÓN DE MATERIALES
echo ========================================================
echo.
echo Este script realizará la instalación completa del sistema
echo en un PC para funcionar en red local.
echo.
echo ⚠️  REQUIERE:
echo    • Conexión a Internet (para descargar dependencias)
echo    • Permisos de Administrador (para configurar red)
echo.
pause

echo.
echo 📋 PASO 1/4: Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado
    echo.
    echo 📥 INSTALACIÓN REQUERIDA:
    echo 1. Vaya a: https://python.org/downloads/
    echo 2. Descargue Python 3.13+ para Windows
    echo 3. Durante instalación, marque "Add Python to PATH"
    echo 4. Reinicie este script después de instalar
    echo.
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo 📋 PASO 2/4: Instalando dependencias...
pip install --upgrade pip >nul
if exist requirements.txt (
    pip install -r requirements.txt
    echo ✅ Dependencias instaladas
) else (
    pip install Flask==3.1.2 Werkzeug==3.1.2 openpyxl==3.1.5
    echo ✅ Dependencias instaladas manualmente
)

echo.
echo 📋 PASO 3/4: Configurando firewall para red...
echo ⚠️  Se solicitarán permisos de administrador
netsh advfirewall firewall delete rule name="Gestión Materiales - Puerto 5000" >nul 2>&1
netsh advfirewall firewall add rule name="Gestión Materiales - Puerto 5000" dir=in action=allow protocol=TCP localport=5000
if %errorlevel% equ 0 (
    echo ✅ Firewall configurado correctamente
) else (
    echo ⚠️  Error configurando firewall (puede requerir permisos de admin)
)

echo.
echo 📋 PASO 4/4: Verificando base de datos...
if exist "..\materiales.db" (
    echo ✅ Base de datos de materiales encontrada
) else (
    echo ⚠️  Base de datos de materiales se creará automáticamente
)

if exist "..\operarios.db" (
    echo ✅ Base de datos de operarios encontrada
) else (
    echo ⚠️  Base de datos de operarios se creará automáticamente
)

echo.
echo ========================================================
echo   ✅ INSTALACIÓN COMPLETADA
echo ========================================================
echo.
echo 🚀 Para iniciar la aplicación:
echo    • Ejecute: iniciar_app.bat
echo    • O ejecute: python app.py
echo.
echo 🌐 Para acceso en red:
echo    • La aplicación mostrará las direcciones disponibles
echo    • Otros PCs usarán: http://[IP-DE-ESTE-PC]:5000
echo.
echo 👤 Usuario administrador por defecto: 999 (sin PIN)
echo.
pause