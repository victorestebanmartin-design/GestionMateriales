@echo off
title Instalar dependencias Agente Excel
echo.
echo ============================================================
echo   Instalando dependencias del Agente Bajas Excel
echo ============================================================
echo.
echo  Comprobando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  Python no encontrado. Intentando instalar con winget...
    echo.
    winget --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] winget no esta disponible en este equipo.
        echo         Descarga Python manualmente de https://www.python.org/downloads/
        echo         Marca "Add Python to PATH" durante la instalacion.
        pause
        exit /b 1
    )
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo [ERROR] La instalacion de Python fallo.
        echo         Puede que IT haya bloqueado winget o no haya conexion a internet.
        echo         Contacta con IT o instala Python manualmente desde https://www.python.org/downloads/
        pause
        exit /b 1
    )
    echo.
    echo  Python instalado. Actualizando PATH para esta sesion...
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
    python --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo   Python se ha instalado correctamente.
        echo   Cierra esta ventana y vuelve a abrir INSTALAR_AGENTE.bat
        echo   para que Windows reconozca el nuevo Python en el PATH.
        echo ============================================================
        pause
        exit /b 0
    )
)
python --version
echo.
echo  Instalando paquetes necesarios...
python -m pip install --upgrade pip
python -m pip install pywin32 requests
echo.
echo  Configurando pywin32...
python -m pywin32_postinstall -install 2>nul
echo.
echo ============================================================
echo   Listo. Ahora puedes ejecutar AGENTE_EXCEL.bat
echo ============================================================
pause
