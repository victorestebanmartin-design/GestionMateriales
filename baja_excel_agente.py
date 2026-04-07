#!/usr/bin/env python3
"""
Agente Bajas Excel — PC cliente.

Conecta al servidor via HTTP, espera solicitudes del admin y ejecuta
las bajas en el Excel abierto en este PC.

Uso:
    python baja_excel_agente.py          → arranca el agente (pide config si es la 1ª vez)
    python baja_excel_agente.py --config → fuerza reconfiguración URL/token
"""

import sys
import os
import time
import json
import argparse
import threading

# ── Configuración ─────────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agente_config.json")
POLL_INTERVAL = 5        # segundos entre consultas al servidor
PAUSA_ENTRE_BAJAS = 2.0  # segundos entre cada baja en Excel

MAPEO_ESTADO = {
    "gastado":  1,
    "retirado": 1,
}


# ── Gestión de configuración ──────────────────────────────────────────────────

def cargar_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def guardar_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def pedir_config():
    print()
    print("=" * 60)
    print("  CONFIGURACIÓN INICIAL DEL AGENTE")
    print("=" * 60)
    print("  Esta configuración se guarda y no se vuelve a pedir.")
    print()
    print("  Ejemplo de URL del servidor: http://192.168.1.103:5000")
    url = input("  URL del servidor: ").strip().rstrip("/")
    if not url.startswith("http"):
        url = "http://" + url
    token = input("  Contraseña admin (o número de usuario admin): ").strip()
    cfg = {"server_url": url, "token": token}
    guardar_config(cfg)
    print()
    print("  ✓ Configuración guardada en agente_config.json")
    print()
    return cfg


def obtener_config(forzar=False):
    cfg = cargar_config()
    if forzar or not cfg.get("server_url") or not cfg.get("token"):
        cfg = pedir_config()
    return cfg


# ── Cliente HTTP ──────────────────────────────────────────────────────────────

def _headers(token):
    return {"Authorization": f"Bearer {token}"}


def api_get(url, token, timeout=10):
    import requests
    return requests.get(url, headers=_headers(token), timeout=timeout)


def api_post(url, token, data=None, timeout=10):
    import requests
    return requests.post(url, headers=_headers(token), json=data or {}, timeout=timeout)


def poll(server_url, token):
    """Devuelve True si hay solicitud pendiente para el agente."""
    try:
        r = api_get(f"{server_url}/api/agente/poll", token)
        if r.status_code == 200:
            return r.json().get("hay_solicitud", False)
    except Exception:
        pass
    return False


def hay_cancelacion(server_url, token):
    try:
        r = api_get(f"{server_url}/api/agente/cancelado", token)
        if r.status_code == 200:
            return r.json().get("cancelado", False)
    except Exception:
        pass
    return False


def obtener_pendientes(server_url, token):
    try:
        r = api_get(f"{server_url}/api/agente/pendientes", token)
        if r.status_code == 200:
            return r.json().get("pendientes", [])
    except Exception as e:
        print(f"  [!] Error obteniendo pendientes: {e}")
    return []


def iniciar_en_servidor(server_url, token):
    try:
        api_post(f"{server_url}/api/agente/iniciar", token)
    except Exception:
        pass


def marcar_uno_en_servidor(server_url, token, mat_id):
    try:
        r = api_post(f"{server_url}/api/agente/marcar_uno/{mat_id}", token)
        return r.status_code == 200
    except Exception as e:
        print(f"  [!] Error marcando material {mat_id}: {e}")
    return False


def completar_en_servidor(server_url, token, salida=""):
    try:
        api_post(f"{server_url}/api/agente/completar", token, {"salida": salida})
    except Exception:
        pass


def reportar_error_en_servidor(server_url, token, mensaje):
    try:
        api_post(f"{server_url}/api/agente/error", token, {"mensaje": mensaje})
    except Exception:
        pass


# ── Automatización Excel (igual que baja_excel.py) ───────────────────────────

def get_excel_instance():
    try:
        import win32com.client
        xl = win32com.client.GetActiveObject("Excel.Application")
        return xl
    except ImportError:
        print("[ERROR] pywin32 no está instalado.")
        print("        Ejecuta INSTALAR_AGENTE.bat primero.")
        sys.exit(1)
    except Exception:
        print("[ERROR] No se encontró Excel abierto.")
        print("        Abre el archivo Excel con la macro DAR_DE_BAJA antes de ejecutar este script.")
        return None


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

    # Intentar flujo MERAK KB primero
    hilo_semi = threading.Thread(target=_hilo_semi_auto, args=(codigo, parar), daemon=True)
    hilo_semi.start()

    t = threading.Thread(target=_enviar_secuencia, daemon=True)
    t.start()

    try:
        xl.Application.Run("DAR_DE_BAJA")
        parar.set()
        return True
    except Exception as e:
        parar.set()
        err = str(e)
        if "-2146788248" in err:
            print(f"         [i] Código no encontrado en Excel — marcando como procesado.")
            return True
        print(f"         [!] Error al ejecutar macro: {e}")
        return False


# ── Bucle principal ───────────────────────────────────────────────────────────

def procesar_solicitud(server_url, token):
    xl = get_excel_instance()
    if xl is None:
        reportar_error_en_servidor(server_url, token, "Excel no está abierto en el PC cliente")
        return

    iniciar_en_servidor(server_url, token)
    pendientes = obtener_pendientes(server_url, token)

    if not pendientes:
        print("  [i] No hay bajas pendientes.")
        completar_en_servidor(server_url, token, "Sin bajas pendientes")
        return

    total = len(pendientes)
    procesados = 0
    errores = 0
    lineas_log = []

    print(f"\n  Procesando {total} baja(s)...\n")

    for i, m in enumerate(pendientes, 1):
        # Comprobar si el admin ha cancelado
        if hay_cancelacion(server_url, token):
            msg = f"Detenido por el admin tras {procesados}/{total} bajas"
            print(f"\n  [!] {msg}")
            reportar_error_en_servidor(server_url, token, msg)
            return

        desc = (m.get("descripcion") or "Sin descripción")[:40]
        print(f"  [{i}/{total}] {m['codigo']}  ({m['estado']})  {desc}")
        lineas_log.append(f"[{i}/{total}] {m['codigo']} ({m['estado']})")

        ok = ejecutar_baja_excel(xl, m["codigo"], m["estado"])
        if ok:
            if marcar_uno_en_servidor(server_url, token, m["id"]):
                procesados += 1
                print(f"         ✓ Procesado.")
                lineas_log[-1] += " ✓"
            else:
                errores += 1
                print(f"         [!] Error al confirmar en servidor.")
                lineas_log[-1] += " (error servidor)"
        else:
            errores += 1
            print(f"         ✗ Error en Excel.")
            lineas_log[-1] += " ✗"

        time.sleep(PAUSA_ENTRE_BAJAS)

    resumen = f"Procesados: {procesados}/{total}  Errores: {errores}"
    print(f"\n{'─'*60}")
    print(f"  {resumen}")
    print(f"{'─'*60}\n")

    salida = "\n".join(lineas_log) + f"\n{resumen}"
    completar_en_servidor(server_url, token, salida)


def bucle_principal(server_url, token):
    print()
    print("=" * 60)
    print("  AGENTE BAJAS EXCEL — en espera de solicitudes")
    print(f"  Servidor: {server_url}")
    print("  Pulsa Ctrl+C para detener")
    print("=" * 60)
    print()

    while True:
        try:
            if poll(server_url, token):
                print(f"  [{time.strftime('%H:%M:%S')}] Solicitud recibida — procesando...")
                procesar_solicitud(server_url, token)
                print(f"  [{time.strftime('%H:%M:%S')}] En espera de nueva solicitud...")
            else:
                sys.stdout.write(f"\r  [{time.strftime('%H:%M:%S')}] Esperando solicitud...")
                sys.stdout.flush()
            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n  Agente detenido por el usuario.")
            break
        except Exception as e:
            print(f"\n  [!] Error inesperado: {e}")
            time.sleep(POLL_INTERVAL)


# ── Entrada ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Agente Bajas Excel")
    parser.add_argument("--config", action="store_true", help="Forzar reconfiguración")
    args = parser.parse_args()

    cfg = obtener_config(forzar=args.config)
    server_url = cfg["server_url"]
    token = cfg["token"]

    # Verificar conexión al servidor
    print(f"  Verificando conexión con {server_url}...")
    try:
        import requests
        r = requests.get(f"{server_url}/api/agente/poll",
                         headers=_headers(token), timeout=5)
        if r.status_code == 401:
            print("  [ERROR] Token/contraseña incorrectos.")
            print("  Ejecuta con --config para reconfigurar.")
            sys.exit(1)
        elif r.status_code != 200:
            print(f"  [AVISO] El servidor respondió con código {r.status_code}.")
        else:
            print("  ✓ Conexión OK")
    except Exception as e:
        print(f"  [ERROR] No se pudo conectar al servidor: {e}")
        print("  Comprueba que el servidor está arriba y la URL es correcta.")
        print("  Ejecuta con --config para reconfigurar.")
        input("\n  Pulsa Enter para salir...")
        sys.exit(1)

    bucle_principal(server_url, token)


if __name__ == "__main__":
    main()
