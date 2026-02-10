@echo off
chcp 65001 >nul
title Preparar Paquete Completo - Gestión de Materiales

echo.
echo =========================================================
echo   PREPARAR PAQUETE COMPLETO - GESTIÓN DE MATERIALES
echo =========================================================
echo.
echo 🎯 Este script prepara el paquete completo para PC sin Python
echo    Instala dependencias en Python portable y crea ejecutables
echo.
echo ⚠️  REQUIERE:
echo    • Haber ejecutado: descargar_python_portable.bat
echo    • Conexión a Internet (para pip install)
echo.
pause

echo.
echo 📋 VERIFICACIÓN: Comprobando Python portable...
if not exist "python_portable\python.exe" (
    echo ❌ Python portable no encontrado
    echo 💡 Ejecute primero: descargar_python_portable.bat
    pause
    exit /b 1
)
echo ✅ Python portable encontrado

echo.
echo 📋 PASO 1/4: Configurando pip en Python portable...
echo ⏳ Instalando pip...
python_portable\python.exe python_portable\get-pip.py --no-warn-script-location
if %errorlevel% neq 0 (
    echo ❌ Error instalando pip
    pause
    exit /b 1
)
echo ✅ pip instalado correctamente

echo.
echo 📋 PASO 2/4: Instalando dependencias en Python portable...
echo ⏳ Instalando Flask, Werkzeug, openpyxl...

:: Instalar desde paquetes offline si existen, sino desde internet
if exist "offline_packages" (
    echo 📦 Usando paquetes offline...
    python_portable\python.exe -m pip install --no-index --find-links offline_packages Flask Werkzeug openpyxl --target python_portable\Lib\site-packages --no-warn-script-location
) else (
    echo 🌐 Descargando desde internet...
    python_portable\python.exe -m pip install Flask==3.1.2 Werkzeug==3.1.2 openpyxl==3.1.5 --target python_portable\Lib\site-packages --no-warn-script-location
)

if %errorlevel% neq 0 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)
echo ✅ Dependencias instaladas

echo.
echo 📋 PASO 3/4: Creando estructura portable...

:: Crear directorio de aplicación portable
if not exist "GestionMateriales_Portable" mkdir GestionMateriales_Portable

:: Copiar Python portable
echo ⏳ Copiando Python portable...
xcopy "python_portable" "GestionMateriales_Portable\python" /E /I /Y >nul

:: Copiar aplicación
echo ⏳ Copiando aplicación...
copy "app.py" "GestionMateriales_Portable\" >nul
copy "requirements.txt" "GestionMateriales_Portable\" >nul

:: Copiar base de datos si existe
if exist "database" (
    xcopy "database" "GestionMateriales_Portable\database" /E /I /Y >nul
    echo ✅ Base de datos copiada
) else (
    mkdir "GestionMateriales_Portable\database" >nul
    echo ✅ Directorio de base de datos creado
)

echo ✅ Estructura portable creada

echo.
echo 📋 PASO 4/4: Creando scripts de ejecución...

:: Script para ejecutar la aplicación
echo @echo off > GestionMateriales_Portable\INICIAR_APP.bat
echo chcp 65001 ^>nul >> GestionMateriales_Portable\INICIAR_APP.bat
echo title Gestión de Materiales - Aplicación Portable >> GestionMateriales_Portable\INICIAR_APP.bat
echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo ================================================================ >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo                    GESTIÓN DE MATERIALES >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo                      Versión Portable >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo ================================================================ >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🚀 Iniciando aplicación portable... >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🐍 Usando Python embebido (no requiere instalación) >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo ⏳ Detectando IP local... >> GestionMateriales_Portable\INICIAR_APP.bat
echo for /f "tokens=2 delims=:" %%%%a in ('ipconfig ^^^| findstr /c:"IPv4"'^) do ^( >> GestionMateriales_Portable\INICIAR_APP.bat
echo     set "ip=%%%%a" >> GestionMateriales_Portable\INICIAR_APP.bat
echo     goto :found >> GestionMateriales_Portable\INICIAR_APP.bat
echo ^) >> GestionMateriales_Portable\INICIAR_APP.bat
echo :found >> GestionMateriales_Portable\INICIAR_APP.bat
echo set ip=%%ip:~1%% >> GestionMateriales_Portable\INICIAR_APP.bat
echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🌐 Accesos disponibles: >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   - Local: http://localhost:5000 >> GestionMateriales_Portable\INICIAR_APP.bat
echo if defined ip echo   - Red: http://%%ip%%:5000 >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🔑 ACCESO ADMINISTRADOR: >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   Usuario: 999 >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   PIN: ^(dejar en blanco^) >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🌟 Características: >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   ✅ Funciona SIN Internet >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   ✅ NO requiere instalar Python >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   ✅ Acceso desde red local >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo   ✅ Exportación Excel offline >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo ⚠️  Para cerrar: Presiona Ctrl+C en esta ventana >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo ================================================================ >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo Abriendo navegador en 3 segundos... >> GestionMateriales_Portable\INICIAR_APP.bat
echo timeout /t 3 /nobreak ^>nul >> GestionMateriales_Portable\INICIAR_APP.bat
echo start "" http://localhost:5000 >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🟢 Aplicación iniciada - Mantén esta ventana abierta >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo python\python.exe app.py >> GestionMateriales_Portable\INICIAR_APP.bat
echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo. >> GestionMateriales_Portable\INICIAR_APP.bat
echo echo 🔴 Aplicación cerrada >> GestionMateriales_Portable\INICIAR_APP.bat
echo pause >> GestionMateriales_Portable\INICIAR_APP.bat

:: Script de configuración firewall (opcional)
echo @echo off > GestionMateriales_Portable\CONFIGURAR_RED.bat
echo chcp 65001 ^>nul >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo title Configurar Red - Gestión de Materiales >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo ========================================================== >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo   CONFIGURACIÓN DE RED - GESTIÓN DE MATERIALES >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo ========================================================== >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo 🔧 Este script configura el firewall para acceso en red >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo ⚠️  REQUIERE PERMISOS DE ADMINISTRADOR >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo pause >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo 🔥 Configurando firewall... >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo netsh advfirewall firewall delete rule name="Gestión Materiales - Puerto 5000" ^>nul 2^>^&1 >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo netsh advfirewall firewall add rule name="Gestión Materiales - Puerto 5000" dir=in action=allow protocol=TCP localport=5000 >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo if %%errorlevel%% equ 0 ^( >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo     echo ✅ Firewall configurado correctamente >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo     echo 🌐 La aplicación será accesible desde otros PCs en la red >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo ^) else ^( >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo     echo ❌ Error configurando firewall >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo     echo 💡 Ejecute como administrador o configure manualmente >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo ^) >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo echo. >> GestionMateriales_Portable\CONFIGURAR_RED.bat
echo pause >> GestionMateriales_Portable\CONFIGURAR_RED.bat

echo ✅ Scripts de ejecución creados

echo.
echo =========================================================
echo   ✅ PAQUETE PORTABLE COMPLETADO
echo =========================================================
echo.
echo 📁 Ubicación: GestionMateriales_Portable\
echo 📦 Tamaño aproximado: ~50-70 MB
echo.
echo 📋 Contenido del paquete:
echo   • 🐍 Python embebido (no requiere instalación)
echo   • 📱 Aplicación completa
echo   • 📊 Base de datos (si existe)
echo   • 🚀 INICIAR_APP.bat (ejecutar aplicación)
echo   • 🌐 CONFIGURAR_RED.bat (acceso en red)
echo.
echo 💾 INSTRUCCIONES PARA EL PC DESTINO:
echo   1. Copie toda la carpeta GestionMateriales_Portable
echo   2. Ejecute INICIAR_APP.bat
echo   3. Si necesita acceso en red, ejecute CONFIGURAR_RED.bat como admin
echo.
echo 🌟 Funciona completamente OFFLINE - Sin internet ni Python
echo.
pause