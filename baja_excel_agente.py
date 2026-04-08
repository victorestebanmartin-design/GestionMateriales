#!/usr/bin/env python3
"""
Automatización LOCAL de Excel — sin acceso a red.

Este script es llamado por agente_excel.ps1 para cada baja.
PowerShell gestiona el HTTP; Python solo automatiza Excel via COM (IPC local).

Uso (llamado desde agente_excel.ps1):
    python baja_excel_agente.py --codigo 1234567 --estado gastado

Exit code: 0 = OK, 1 = error
"""

import sys
import os
import time
import argparse
import threading

MAPEO_ESTADO = {
    "gastado":  1,
    "retirado": 1,
}


# ── Automatización Excel (COM local, sin red) ─────────────────────────────────

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


# ── Entrada ───────────────────────────────────────────────────────────────────

def main():
    """
    Llamado por agente_excel.ps1 para procesar UNA baja en Excel.
    PowerShell gestiona el HTTP; aquí solo se automatiza Excel localmente.
    """
    parser = argparse.ArgumentParser(description="Automatización local Excel — una baja")
    parser.add_argument("--codigo", required=True, help="Código del material")
    parser.add_argument("--estado", default="gastado", help="Estado del material")
    args = parser.parse_args()

    xl = get_excel_instance()
    if xl is None:
        sys.exit(1)

    ok = ejecutar_baja_excel(xl, args.codigo, args.estado)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
