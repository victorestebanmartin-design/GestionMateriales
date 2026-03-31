@echo off
:: Ir siempre a la carpeta donde esta este .bat (aunque se ejecute como admin desde System32)
cd /d "%~dp0"
title Instalador - Gestion de Materiales
color 0A

:: ── AVISO: NO ejecutar como Administrador (winget no funciona en contexto elevado) ──
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo   ATENCION: Estás ejecutando como Administrador
    echo ================================================
    echo.
    echo  Este instalador NO debe ejecutarse como Admin.
    echo  winget no funciona en modo elevado en Windows.
    echo.
    echo  Por favor:
    echo    1. Cierra esta ventana
    echo    2. Haz doble clic en INSTALAR.bat SIN
    echo       seleccionar "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

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

:: ── Python ───────────────────────────────────────────────────────────────────
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% equ 0 goto python_ok

:: Intentar winget primero
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Instalando Python 3.12 con winget...
    winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    goto python_instalado
)

:: Sin winget: descargar directamente
echo winget no disponible. Descargando Python 3.12 directamente...
powershell -NoProfile -Command "try { $f='%TEMP%\python312.exe'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe' -OutFile $f -UseBasicParsing; Start-Process $f -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1' -Wait; Write-Host 'Python instalado.' } catch { Write-Host '[ERROR] No se pudo descargar Python. Instalalo manualmente desde https://www.python.org/downloads/'; exit 1 }"
if %errorlevel% neq 0 ( pause & exit /b 1 )

:python_instalado
echo Python instalado. Necesitas reabrir esta ventana para que surta efecto.
goto continuar_con_git

:python_ok
echo Python verificado.

:continuar_con_git
:: ── Git ──────────────────────────────────────────────────────────────────────
echo [2/4] Verificando Git...
git --version >nul 2>&1
if %errorlevel% equ 0 goto git_ok

:: Intentar winget primero
winget --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Instalando Git con winget...
    winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
    goto git_instalado
)

:: Sin winget: descargar directamente
echo winget no disponible. Descargando Git directamente...
powershell -NoProfile -Command "try { $f='%TEMP%\git_installer.exe'; Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/Git-2.47.1.2-64-bit.exe' -OutFile $f -UseBasicParsing; Start-Process $f -ArgumentList '/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=icons,ext\reg\shellhere,assoc,assoc_sh' -Wait; Write-Host 'Git instalado.' } catch { Write-Host '[ERROR] No se pudo descargar Git. Instalalo manualmente desde https://git-scm.com/download/win'; exit 1 }"
if %errorlevel% neq 0 ( pause & exit /b 1 )

:git_instalado
echo Git instalado.

:git_ok
echo Git verificado.

:: ── Refrescar PATH completo desde el registro del sistema ────────────────────
:: winget actualiza el PATH en el registro pero no en la sesion CMD actual.
:: Leemos el PATH del registro y lo aplicamos a esta sesion.
echo Actualizando variables de entorno...
for /f "usebackq delims=" %%P in (`powershell -NoProfile -Command "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User')"`) do set "PATH=%%P"

:: ── Clonar o actualizar repo ──────────────────────────────────────────────────
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
