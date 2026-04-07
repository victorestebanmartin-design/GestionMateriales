@echo off
title Agente Bajas Excel
echo.
echo ============================================================
echo   Agente Bajas Excel
echo ============================================================
echo.

REM Buscar python en las rutas mas habituales
python --version >nul 2>&1
if not errorlevel 1 goto :python_ok

REM Intentar py launcher (instalador oficial)
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py
    goto :python_ok_py
)

echo  [ERROR] Python no encontrado.
echo  Ejecuta primero INSTALAR_AGENTE.bat para instalarlo.
pause
exit /b 1

:python_ok
set PYTHON=python
goto :run

:python_ok_py
set PYTHON=py

:run
echo  Python encontrado:
%PYTHON% --version
echo.

REM Verificar que requests y pywin32 estan instalados
%PYTHON% -c "import requests, win32com.client" >nul 2>&1
if errorlevel 1 (
    echo  [AVISO] Faltan dependencias. Ejecutando instalacion automatica...
    %PYTHON% -m pip install --quiet pywin32 requests
    %PYTHON% -m pywin32_postinstall -install >nul 2>&1
    echo  Dependencias instaladas.
    echo.
)

echo  Arrancando agente...
echo  (Pulsa Ctrl+C para detener)
echo.
%PYTHON% "%~dp0baja_excel_agente.py" %*

echo.
echo  El agente se ha detenido.
pause
