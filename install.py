#!/usr/bin/env python3
"""
Instalador de GestionMateriales
Funciona en Windows, macOS y Linux.
Uso: python install.py
"""
import sys
import os
import subprocess
import platform

MIN_PYTHON = (3, 10)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, ".venv")

def header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def step(n, total, text):
    print(f"\n[{n}/{total}] {text}")

def ok(text):
    print(f"  v  {text}")

def error(text):
    print(f"  X  {text}")

def warn(text):
    print(f"  !  {text}")

def webview2_instalado():
    """Comprueba si WebView2 Runtime está instalado (solo Windows)."""
    try:
        import winreg
        claves = [
            r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
        ]
        for clave in claves:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave):
                    return True
            except FileNotFoundError:
                pass
        # También comprobar en HKCU
        for clave in claves:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, clave):
                    return True
            except FileNotFoundError:
                pass
        return False
    except ImportError:
        return True  # No Windows, no aplica

def instalar_webview2():
    """Descarga e instala WebView2 Runtime de forma silenciosa."""
    import urllib.request
    import tempfile
    url = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
    installer = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebview2Setup.exe")
    print("  Descargando WebView2 Runtime (~2 MB)…")
    try:
        urllib.request.urlretrieve(url, installer)
        print("  Instalando (modo silencioso)…")
        result = subprocess.run([installer, "/silent", "/install"])
        if result.returncode == 0:
            ok("WebView2 Runtime instalado correctamente.")
        else:
            warn(f"El instalador devolvió código {result.returncode}. Puede que ya estuviera instalado.")
    except Exception as e:
        warn(f"No se pudo descargar WebView2 automáticamente: {e}")
        print("  Descárgalo manualmente desde:")
        print("  https://developer.microsoft.com/es-es/microsoft-edge/webview2/")

# ── Paso 0: verificar versión de Python ──────────────────────────────────────
header("Instalador – Gestión de Materiales")
print(f"Python detectado: {sys.version}")

if sys.version_info < MIN_PYTHON:
    error(f"Se requiere Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} o superior.")
    sys.exit(1)
ok(f"Python {sys.version_info.major}.{sys.version_info.minor} — OK")

IS_WINDOWS = platform.system() == "Windows"
VENV_PYTHON = os.path.join(VENV_DIR, "Scripts" if IS_WINDOWS else "bin", "python")
# Usar python -m pip en vez de pip.exe para evitar bloqueos de directiva de grupo
VENV_PIP    = None  # no se usa directamente
TOTAL = 5

# ── Paso 0b: WebView2 Runtime (solo Windows) ─────────────────────────────────
if IS_WINDOWS:
    step("0b", TOTAL, "Comprobando WebView2 Runtime (necesario para la ventana nativa)…")
    if webview2_instalado():
        ok("WebView2 Runtime ya está instalado.")
    else:
        warn("WebView2 Runtime NO encontrado. Instalando automáticamente…")
        instalar_webview2()

# ── Paso 1: crear entorno virtual ────────────────────────────────────────────
step(1, TOTAL, "Creando entorno virtual (.venv)…")
if os.path.isdir(VENV_DIR):
    ok(".venv ya existe, se reutiliza.")
else:
    result = subprocess.run([sys.executable, "-m", "venv", VENV_DIR])
    if result.returncode != 0:
        error("No se pudo crear el entorno virtual.")
        sys.exit(1)
    ok(".venv creado correctamente.")

# ── Paso 2: actualizar pip ────────────────────────────────────────────────────
step(2, TOTAL, "Actualizando pip…")
subprocess.run([VENV_PYTHON, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])
ok("pip actualizado.")

# ── Paso 3: instalar dependencias ─────────────────────────────────────────────
step(3, TOTAL, "Instalando dependencias (requirements.txt)…")
req_file = os.path.join(BASE_DIR, "requirements.txt")
result = subprocess.run([VENV_PYTHON, "-m", "pip", "install", "-r", req_file])
if result.returncode != 0:
    error("Error instalando dependencias. Comprueba tu conexión a Internet.")
    sys.exit(1)
ok("Dependencias instaladas.")

# ── Paso 4: inicializar bases de datos ────────────────────────────────────────
step(4, TOTAL, "Inicializando bases de datos…")
db_mat = os.path.join(BASE_DIR, "database", "materiales.db")
db_ops = os.path.join(BASE_DIR, "database", "operarios.db")

if os.path.isfile(db_mat) and os.path.isfile(db_ops):
    ok("Bases de datos ya existen, no se tocan.")
else:
    script_db = os.path.join(BASE_DIR, "database", "create_herramientas_db.py")
    if os.path.isfile(script_db):
        result = subprocess.run([VENV_PYTHON, script_db])
        if result.returncode != 0:
            warn("El script de BD devolvió error, pero continuamos.")
        else:
            ok("Bases de datos creadas.")
    else:
        # La app las crea sola al arrancar por primera vez
        ok("Se crearán automáticamente al primer arranque.")

# ── Paso 5: crear script de arranque ─────────────────────────────────────────
step(5, TOTAL, "Creando script de arranque…")

if IS_WINDOWS:
    start_bat = os.path.join(BASE_DIR, "start.bat")
    if not os.path.isfile(start_bat):
        with open(start_bat, "w", encoding="utf-8") as f:
            f.write('@echo off\r\n')
            f.write('title Gestión de Materiales\r\n')
            f.write('call .venv\\Scripts\\activate.bat\r\n')
            f.write('python run_app_window.py\r\n')
            f.write('pause\r\n')
        ok("start.bat creado.")
    else:
        ok("start.bat ya existe.")
else:
    start_sh = os.path.join(BASE_DIR, "start.sh")
    if not os.path.isfile(start_sh):
        with open(start_sh, "w", encoding="utf-8") as f:
            f.write('#!/bin/bash\n')
            f.write('source .venv/bin/activate\n')
            f.write('python run_app_window.py\n')
        os.chmod(start_sh, 0o755)
        ok("start.sh creado.")
    else:
        ok("start.sh ya existe.")

# ── Finalizado ────────────────────────────────────────────────────────────────
import socket
try:
    ip = socket.gethostbyname(socket.gethostname())
except Exception:
    ip = "127.0.0.1"

header("¡Instalación completada!")
print(f"""
  Para ARRANCAR la aplicación:

    Windows:  start.bat  (doble clic)
    Otros:    ./start.sh
    Manual:   .venv/Scripts/python run_app_window.py

  La app estará disponible en:
    • http://127.0.0.1:5000
    • http://{ip}:5000  (acceso desde la red local)

  Credenciales por defecto:
    • Admin:       número 999999
    • Para cambiarlas, edita las variables ADMIN_PASSWORD,
      ALMACEN_PIN, OPERARIO_PIN en app.py o como variables
      de entorno.
""")
