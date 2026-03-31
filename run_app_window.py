"""
Ejecuta la aplicación de Gestión de Materiales en una ventana nativa
sin barra de navegador - Modo maximizado con botones flotantes
"""
import sys
import platform
import subprocess

def _check_webview2():
    """Comprueba si WebView2 Runtime está instalado y lo instala si falta."""
    if platform.system() != "Windows":
        return
    try:
        import winreg
        claves = [
            r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
            r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
        ]
        for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            for clave in claves:
                try:
                    with winreg.OpenKey(hive, clave):
                        return  # encontrado
                except FileNotFoundError:
                    pass
        # No encontrado — intentar instalar automáticamente
        print("WebView2 Runtime no encontrado. Instalando automáticamente...")
        import urllib.request, tempfile, os
        url = "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
        installer = os.path.join(tempfile.gettempdir(), "MicrosoftEdgeWebview2Setup.exe")
        try:
            urllib.request.urlretrieve(url, installer)
            result = subprocess.run([installer, "/silent", "/install"])
            if result.returncode == 0:
                print("WebView2 Runtime instalado correctamente.")
            else:
                print(f"Instalador devolvió código {result.returncode} (puede que ya estuviera instalado).")
        except Exception as e:
            print(f"\n[ERROR] No se pudo instalar WebView2 automáticamente: {e}")
            print("Por favor, descárgalo manualmente desde:")
            print("  https://developer.microsoft.com/es-es/microsoft-edge/webview2/")
            input("\nPulsa ENTER para salir...")
            sys.exit(1)
    except ImportError:
        pass  # No Windows

_check_webview2()

import webview
import threading
import time
import socket
from app import app, init_db


def get_local_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "localhost"


def start_flask():
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)


# API expuesta al JavaScript de la ventana
class VentanaAPI:
    def __init__(self):
        self._window = None

    def set_window(self, win):
        self._window = win

    def cerrar(self):
        """Cierra la aplicación desde el botón flotante"""
        if self._window:
            self._window.destroy()

    def toggleFullscreen(self):
        """Activa/desactiva pantalla completa desde el botón flotante"""
        if self._window:
            self._window.toggle_fullscreen()


# JS que inyecta un panel flotante con botones Cerrar y Pantalla completa
BOTONES_FLOTANTES_JS = """
(function() {
    if (document.getElementById('_wv_controles')) return;

    var bar = document.createElement('div');
    bar.id = '_wv_controles';
    bar.style.cssText = [
        'position:fixed',
        'top:6px',
        'right:8px',
        'z-index:2147483647',
        'display:flex',
        'gap:4px',
        'opacity:0.25',
        'transition:opacity 0.2s',
        'pointer-events:auto'
    ].join(';');

    bar.addEventListener('mouseenter', function(){ bar.style.opacity='1'; });
    bar.addEventListener('mouseleave', function(){ bar.style.opacity='0.25'; });

    function crearBtn(texto, color, accion) {
        var b = document.createElement('button');
        b.textContent = texto;
        b.title = accion === 'cerrar' ? 'Cerrar aplicacion (click)' : 'Pantalla completa (click)';
        b.style.cssText = [
            'background:' + color,
            'color:#fff',
            'border:none',
            'border-radius:4px',
            'padding:4px 10px',
            'font-size:14px',
            'font-weight:bold',
            'cursor:pointer',
            'line-height:1',
            'box-shadow:0 2px 6px rgba(0,0,0,0.4)'
        ].join(';');
        b.addEventListener('click', function() {
            if (accion === 'cerrar') {
                window.pywebview.api.cerrar();
            } else {
                window.pywebview.api.toggleFullscreen();
            }
        });
        return b;
    }

    bar.appendChild(crearBtn('⛶', '#555', 'fullscreen'));
    bar.appendChild(crearBtn('✕', '#c0392b', 'cerrar'));
    document.body.appendChild(bar);
})();
"""


def main():
    print("=" * 60)
    print("GESTION DE MATERIALES - MODO VENTANA NATIVA")
    print("=" * 60)

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    print("Esperando a que el servidor este listo...")
    time.sleep(2)

    ip = get_local_ip()
    print(f"Servidor en: http://localhost:5000  |  Red: http://{ip}:5000")
    print("Botones flotantes en esquina superior derecha para Cerrar y Pantalla completa.")
    print("=" * 60)

    api = VentanaAPI()

    window = webview.create_window(
        title='Gestion de Materiales',
        url='http://localhost:5000',
        fullscreen=False,
        resizable=True,
        frameless=False,
        width=1280,
        height=800,
        js_api=api,
    )
    api.set_window(window)

    def on_loaded():
        window.maximize()
        window.evaluate_js(BOTONES_FLOTANTES_JS)

    webview.start(on_loaded)

    print("\nAplicacion cerrada")

if __name__ == '__main__':
    main()
