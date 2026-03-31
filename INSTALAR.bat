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
