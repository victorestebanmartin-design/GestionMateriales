@echo off
:: Ir siempre a la carpeta donde esta este .bat (aunque se ejecute como admin desde System32)
cd /d "%~dp0"
title Instalador - Gestion de Materiales
color 0A

echo.
echo ================================================
echo    INSTALADOR - GESTION DE MATERIALES
echo ================================================
echo.
echo Instalando todo lo necesario, por favor espera...
echo.

:: ── WebView2 Runtime (necesario para la ventana nativa) ─────────────────────
echo [0/4] Comprobando WebView2 Runtime...
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 goto webview2_ok
reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 goto webview2_ok
reg query "HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 goto webview2_ok

echo WebView2 Runtime NO encontrado. Descargando e instalando...
powershell -NoProfile -Command "try { $f='%TEMP%\webview2setup.exe'; Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile $f -UseBasicParsing; Start-Process $f -ArgumentList '/silent /install' -Wait; Write-Host 'WebView2 instalado correctamente.' } catch { Write-Host 'Aviso: no se pudo instalar WebView2 automaticamente. Descargalo desde https://developer.microsoft.com/es-es/microsoft-edge/webview2/' }"

:webview2_ok
echo WebView2 Runtime verificado.
echo.

:: Verificar winget
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] winget no encontrado.
    echo Actualiza Windows desde Windows Update e intentalo de nuevo.
    pause
    exit /b 1
)

:: Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Python 3.12...
    winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
) else (
    echo Python ya instalado.
)

:: Git
echo [2/4] Verificando Git...
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Git...
    winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
    set "PATH=%PATH%;C:\Program Files\Git\cmd"
) else (
    echo Git ya instalado.
)

:: Refrescar PATH
set "PATH=%PATH%;C:\Program Files\Git\cmd"
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312"
set "PATH=%PATH%;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"

:: Clonar o actualizar repo
echo [3/4] Descargando la aplicacion...
if exist GestionMateriales (
    echo La carpeta ya existe, actualizando...
    cd GestionMateriales
    git pull origin main
) else (
    git clone https://github.com/victorestebanmartin-design/GestionMateriales.git
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo descargar la aplicacion.
        echo Comprueba tu conexion a internet e intentalo de nuevo.
        pause
        exit /b 1
    )
    cd GestionMateriales
)

:: Instalar dependencias
echo [4/4] Instalando dependencias y configurando...
python install.py
if %errorlevel% neq 0 (
    echo [ERROR] Fallo durante la instalacion de dependencias.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Instalacion completada con exito!
echo   Para abrir la app: doble clic en
echo   GestionMateriales\start.bat
echo ================================================
echo.
pause
