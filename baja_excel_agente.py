#!/usr/bin/env python3
"""
Agente Bajas Excel — servidor HTTP local en 127.0.0.1:8765

Python NUNCA hace conexiones de red salientes.
Solo escucha en localhost — el EDR/firewall no lo ve.
El navegador (admin panel) actúa de puente:
  - Pide pendientes al servidor  (mismo origen, libre)
  - POST a localhost:8765/ejecutar (loopback, libre)
  - Confirma cada baja al servidor (mismo origen, libre)

Uso: python baja_excel_agente.py
     python baja_excel_agente.py --puerto 8765
"""

import sys
import os
import time
import json
import argparse
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8765
MAPEO_ESTADO = {
    "gastado":  1,
    "retirado": 1,
}


# ── Automatización Excel ──────────────────────────────────────────────────────

def get_excel_instance():
    """Devuelve (xl_object, None) o (None, error_string)."""
    try:
        import win32com.client
        xl = win32com.client.GetActiveObject("Excel.Application")
        return xl, None
    except ImportError:
        return None, "pywin32 no instalado — ejecuta INSTALAR_AGENTE.bat"
    except Exception:
        return None, "Excel no está abierto — ábrelo con la macro DAR_DE_BAJA"


def _activar_dialogo_excel(texto_titulo, timeout=4.0):
    import win32gui
    encontrado = [None]
    texto = texto_titulo.upper()

    def _cb(hwnd, _):
        if encontrado[0]:
            return
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return
            t = win32gui.GetWindowText(hwnd).upper()
            if texto in t:
                encontrado[0] = hwnd
        except Exception:
            pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.2)
        win32gui.EnumWindows(_cb, None)
        if encontrado[0]:
            try:
                win32gui.SetForegroundWindow(encontrado[0])
                time.sleep(0.1)
            except Exception:
                pass
            return encontrado[0]
    return None


def _click_boton_dar_de_baja(timeout=6.0):
    import win32gui
    import win32con
    encontrado = [False]

    def _check_child(hwnd, _):
        if encontrado[0]:
            return
        try:
            txt = win32gui.GetWindowText(hwnd)
            if "DAR" in txt.upper() and "BAJA" in txt.upper():
                win32gui.PostMessage(hwnd, win32con.BM_CLICK, 0, 0)
                encontrado[0] = True
        except Exception:
            pass

    def _check_toplevel(hwnd, _):
        if encontrado[0]:
            return
        try:
            win32gui.EnumChildWindows(hwnd, _check_child, None)
        except Exception:
            pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.2)
        win32gui.EnumWindows(_check_toplevel, None)
        if encontrado[0]:
            return True
    return False


def _click_boton_aceptar(timeout=8.0):
    import win32gui
    import win32con
    TEXTOS = {"ACEPTAR", "OK", "ACCEPT"}
    encontrado = [False]

    def _check_child(hwnd, _):
        if encontrado[0]:
            return
        try:
            txt = win32gui.GetWindowText(hwnd).strip().upper()
            if txt in TEXTOS:
                win32gui.PostMessage(hwnd, win32con.BM_CLICK, 0, 0)
                encontrado[0] = True
        except Exception:
            pass

    def _check_toplevel(hwnd, _):
        if encontrado[0]:
            return
        try:
            if win32gui.IsWindowVisible(hwnd):
                win32gui.EnumChildWindows(hwnd, _check_child, None)
        except Exception:
            pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(0.2)
        win32gui.EnumWindows(_check_toplevel, None)
        if encontrado[0]:
            return True
    return False


def _hilo_semi_auto(codigo, parar_event):
    import pythoncom
    import win32gui
    import win32com.client

    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        deadline = time.time() + 15.0
        hwnd = None
        while not parar_event.is_set() and time.time() < deadline:
            hwnd = win32gui.FindWindow(None, "MERAK KB")
            if hwnd and win32gui.IsWindowVisible(hwnd):
                break
            time.sleep(0.15)

        if not hwnd or parar_event.is_set():
            return

        try:
            win32gui.ShowWindow(hwnd, 9)
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        time.sleep(0.4)

        shell.SendKeys("{TAB}{TAB}", 0)
        time.sleep(0.15)
        shell.SendKeys(str(codigo), 0)
        time.sleep(0.15)
        shell.SendKeys("{TAB}{ENTER}", 0)

        CLASES_MAIN = {'XLMAIN', 'XLDESK', 'EXCEL7'}

        def _hijos_textos(h):
            textos = set()
            def cb(c, _):
                try:
                    t = win32gui.GetWindowText(c).strip().upper()
                    if t:
                        textos.add(t)
                except Exception:
                    pass
            try:
                win32gui.EnumChildWindows(h, cb, None)
            except Exception:
                pass
            return textos

        msgbox_visto = [False]
        deadline2 = time.time() + 8.0
        while not parar_event.is_set() and not msgbox_visto[0] and time.time() < deadline2:
            time.sleep(0.1)
            def _check(h, _):
                if msgbox_visto[0]: return
                try:
                    if not win32gui.IsWindowVisible(h): return
                    if win32gui.GetClassName(h).upper() in CLASES_MAIN: return
                    textos = _hijos_textos(h)
                    if ("ACEPTAR" in textos or "OK" in textos) and \
                       "DAR DE BAJA" not in textos and "SALIR" not in textos:
                        msgbox_visto[0] = True
                except Exception:
                    pass
            win32gui.EnumWindows(_check, None)

        time.sleep(0.1)
        shell.SendKeys("{ENTER}", 0)
        time.sleep(0.5)
        shell.SendKeys("{TAB}{ENTER}", 0)
    finally:
        pythoncom.CoUninitialize()


def ejecutar_baja_excel(xl, codigo, estado):
    import win32com.client
    shell = win32com.client.Dispatch("WScript.Shell")
    opcion = MAPEO_ESTADO.get(estado, 1)
    parar = threading.Event()

    def _enviar_secuencia():
        hwnd = _activar_dialogo_excel("ETIQUETA", timeout=4.0)
        if not hwnd:
            time.sleep(0.8)
        shell.SendKeys("^a" + str(codigo) + "~", 0)

        if opcion == 2:
            time.sleep(1.0)
            import win32gui
            import win32con
            def _bajar_listbox(hwnd_child, _):
                try:
                    cls = win32gui.GetClassName(hwnd_child)
                    if "LISTBOX" in cls.upper():
                        win32gui.PostMessage(hwnd_child, win32con.LB_SETCURSEL, 1, 0)
                except Exception:
                    pass
            def _buscar_form(hwnd_top, _):
                try:
                    win32gui.EnumChildWindows(hwnd_top, _bajar_listbox, None)
                except Exception:
                    pass
            win32gui.EnumWindows(_buscar_form, None)

        ok = _click_boton_dar_de_baja(timeout=6.0)
        if not ok:
            shell.SendKeys("{ENTER}", 0)
        _click_boton_aceptar(timeout=8.0)

    hilo_semi = threading.Thread(target=_hilo_semi_auto, args=(codigo, parar), daemon=True)
    hilo_semi.start()
    t = threading.Thread(target=_enviar_secuencia, daemon=True)
    t.start()

    try:
        xl.Application.Run("DAR_DE_BAJA")
        parar.set()
        return True, None
    except Exception as e:
        parar.set()
        err = str(e)
        if "-2146788248" in err:
            return True, None   # código no encontrado = ya estaba dado de baja
        return False, str(e)


# ── Servidor HTTP local ───────────────────────────────────────────────────────

class AgenteHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        # Solo mostrar en consola si no es el poll de Chrome
        if "/status" not in (args[0] if args else ""):
            print(f"  [{self.client_address[0]}] {fmt % args}")

    def _send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # CORS: el admin panel viene de http://servidor:5000
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            pass  # AbortController del navegador cortó la conexión — ignorar

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            self._send_json({"online": True, "version": "browser-bridge"})
        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        if self.path == "/ejecutar":
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except Exception:
                self._send_json({"ok": False, "error": "JSON inválido"}, 400)
                return

            codigo = str(body.get("codigo", "")).strip()
            estado = str(body.get("estado", "gastado")).strip()

            if not codigo:
                self._send_json({"ok": False, "error": "codigo vacío"}, 400)
                return

            result = get_excel_instance()
            if isinstance(result, tuple):
                xl, err = result
            else:
                xl, err = result, None

            if xl is None:
                self._send_json({"ok": False, "error": err or "Excel no disponible"}, 503)
                return

            ok, err = ejecutar_baja_excel(xl, codigo, estado)
            if ok:
                self._send_json({"ok": True})
            else:
                self._send_json({"ok": False, "error": err or "Error desconocido"})
        else:
            self._send_json({"error": "Not found"}, 404)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--puerto", type=int, default=PORT)
    args = parser.parse_args()

    # Verificar pywin32 al arrancar
    try:
        import win32com.client  # noqa
    except ImportError:
        print("[ERROR] pywin32 no está instalado.")
        print("        Ejecuta INSTALAR_AGENTE.bat primero.")
        input("Pulsa Enter para salir...")
        sys.exit(1)

    server = HTTPServer(("127.0.0.1", args.puerto), AgenteHandler)

    print()
    print("=" * 60)
    print(f"  Agente Bajas Excel — escuchando en localhost:{args.puerto}")
    print("  El navegador (admin panel) se conecta a este puerto.")
    print("  Abre el Excel con las macros ANTES de enviar bajas.")
    print("  Pulsa Ctrl+C para detener.")
    print("=" * 60)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Agente detenido.")


if __name__ == "__main__":
    main()

