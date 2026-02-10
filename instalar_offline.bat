@echo off
chcp 65001 >nul
title Instalación OFFLINE - Gestión de Materiales

echo.
echo =========================================================
echo   INSTALACIÓN OFFLINE - GESTIÓN DE MATERIALES
echo =========================================================
echo.
echo ⚠️  MODO OFFLINE - No requiere conexión a Internet
echo.
echo Este script instalará la aplicación en un PC SIN acceso
echo a Internet usando los paquetes incluidos en el pen drive.
echo.
echo 🔧 REQUIERE:
echo    • Python 3.13+ instalado (desde python.org)
echo    • Permisos de Administrador (para configurar red)
echo.
pause

echo.
echo 📋 PASO 1/4: Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado
    echo.
    echo 🚨 INSTALACIÓN DE PYTHON REQUERIDA:
    echo.
    echo OPCIÓN A - Con Internet:
    echo 1. Vaya a: https://python.org/downloads/
    echo 2. Descargue Python 3.13+ para Windows
    echo 3. Durante instalación, marque "Add Python to PATH"
    echo 4. Reinicie este script después de instalar
    echo.
    echo OPCIÓN B - Sin Internet:
    echo 1. Descargue Python en otro PC con internet
    echo 2. Copie el instalador python-3.13.x-amd64.exe al pen drive
    echo 3. Instálelo en este PC marcando "Add Python to PATH"
    echo 4. Reinicie este script
    echo.
    pause
    exit /b 1
)
echo ✅ Python encontrado

echo.
echo 📋 PASO 2/4: Instalando dependencias OFFLINE...
echo ⏳ Instalando desde paquetes locales...

if exist "offline_packages" (
    python -m pip install --no-index --find-links offline_packages Flask Werkzeug openpyxl
    if %errorlevel% equ 0 (
        echo ✅ Dependencias instaladas correctamente (OFFLINE)
    ) else (
        echo ⚠️  Error instalando dependencias offline
        echo 🔄 Intentando instalación online como respaldo...
        python -m pip install -r requirements.txt
        if %errorlevel% equ 0 (
            echo ✅ Dependencias instaladas (ONLINE)
        ) else (
            echo ❌ Error instalando dependencias
            echo 💡 Verifique conexión a internet o paquetes offline
            pause
            exit /b 1
        )
    )
) else (
    echo ⚠️  Carpeta offline_packages no encontrada
    echo 🔄 Intentando instalación online...
    python -m pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo ✅ Dependencias instaladas (ONLINE)
    ) else (
        echo ❌ Error instalando dependencias
        pause
        exit /b 1
    )
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
    echo 💡 La aplicación funcionará localmente, pero no en red
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
echo =========================================================
echo   ✅ INSTALACIÓN OFFLINE COMPLETADA
echo =========================================================
echo.
echo 🚀 Para iniciar la aplicación:
echo    • Ejecute: iniciar_app.bat
echo    • O ejecute: python app.py
echo.
echo 🌐 Funcionamiento:
echo    • ✅ Funciona SIN conexión a Internet
echo    • ✅ Acceso local: http://127.0.0.1:5000
echo    • ✅ Acceso en red: http://[IP-DE-ESTE-PC]:5000
echo.
echo 👤 Usuario administrador: 999 (sin PIN)
echo.
echo 📊 Funcionalidades disponibles:
echo    • ✅ Gestión completa de materiales
echo    • ✅ Exportación/Importación Excel (OFFLINE)
echo    • ✅ Funcionamiento en red local
echo    • ✅ Panel de administración completo
echo.
pause