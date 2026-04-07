#!/usr/bin/env python3
"""
Automatización de bajas en Excel.

Obtiene los materiales gastados/retirados pendientes de procesar en Excel
y llama al macro DAR_DE_BAJA automáticamente por cada uno.

Uso:
    python baja_excel.py          → modo automático (procesa todos)
    python baja_excel.py --lista  → solo muestra los pendientes sin automatizar
    python baja_excel.py --uno    → procesa de uno en uno con confirmación
"""

import sys
import os
import time
import sqlite3
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_MATERIALES = os.path.join(BASE_DIR, "database", "materiales.db")

ESTADOS_BAJA = ("gastado", "retirado")
PAUSA_ENTRE_BAJAS = 2.0  # segundos entre cada llamada al macro

# ── Mapeo de estado app → opción en el UserForm Excel ────────────────────────
# El UserForm muestra las opciones en este orden (1-based):
#   1 → Material RETIRADO
#   2 → Material NO CONTROLADO
# Ajusta si en tu Excel el orden es distinto.
MAPEO_ESTADO = {
    "gastado":  1,   # Material RETIRADO  (consumido/gastado)
    "retirado": 1,   # Material RETIRADO
}


def _ensure_bajas_table(conn):
    """Crea la tabla bajas si no existe (migración automática)."""
    try:
        conn.execute(
            "ALTER TABLE materiales ADD COLUMN procesado_excel INTEGER DEFAULT 0"
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass  # Columna ya existe
    conn.execute(
        """CREATE TABLE IF NOT EXISTS bajas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo          TEXT,
            descripcion     TEXT,
            estado_original TEXT,
            operario_numero TEXT,
            fecha_baja      TEXT DEFAULT (datetime('now','localtime'))
        )"""
    )
    conn.commit()


def get_pendientes():
    """Devuelve materiales con estado baja que no se han procesado en Excel."""
    conn = sqlite3.connect(DB_MATERIALES)
    conn.row_factory = sqlite3.Row
    _ensure_bajas_table(conn)

    cur = conn.execute(
        """
        SELECT id, codigo, descripcion, estado, operario_numero, fecha_asignacion
        FROM materiales
        WHERE estado IN ({})
          AND (procesado_excel IS NULL OR procesado_excel = 0)
        ORDER BY fecha_asignacion ASC
        """.format(",".join("?" * len(ESTADOS_BAJA))),
        ESTADOS_BAJA,
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def marcar_procesado(material_id: int):
    """Marca un material como procesado en Excel y lo registra en la tabla bajas."""
    conn = sqlite3.connect(DB_MATERIALES)
    _ensure_bajas_table(conn)
    row = conn.execute(
        "SELECT codigo, descripcion, estado, operario_numero FROM materiales WHERE id = ?",
        (material_id,)
    ).fetchone()
    conn.execute(
        "UPDATE materiales SET procesado_excel = 1 WHERE id = ?", (material_id,)
    )
    if row:
        conn.execute(
            """INSERT INTO bajas (codigo, descripcion, estado_original, operario_numero, fecha_baja)
               VALUES (?, ?, ?, ?, datetime('now','localtime'))""",
            (row[0], row[1], row[2], row[3])
        )
    conn.commit()
    conn.close()


def get_excel_instance():
    """Obtiene la instancia de Excel en ejecución via COM."""
    try:
        import win32com.client
        xl = win32com.client.GetActiveObject("Excel.Application")
        return xl
    except ImportError:
        print("[ERROR] pywin32 no está instalado.")
        print("        Ejecuta: .venv\\Scripts\\pip install pywin32")
        sys.exit(1)
    except Exception:
        print("[ERROR] No se encontró Excel abierto.")
        print("        Abre el archivo Excel con la macro DAR_DE_BAJA antes de ejecutar este script.")
        sys.exit(1)


def _activar_dialogo_excel(texto_titulo, timeout=4.0):
    """
    Busca una ventana de diálogo de Excel que contenga texto_titulo,
    la pone en primer plano y devuelve su hwnd. None si no la encontró.
    """
    import win32gui
    import win32con

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
    """
    Busca el botón 'DAR DE BAJA' en cualquier ventana visible y envía BM_CLICK.
    Devuelve True si lo encontró y clicó.
    """
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
    """
    Busca y clica cualquier botón 'Aceptar' / 'OK' / 'Aceptar' que aparezca
    en un MsgBox de Excel (p.ej. "Etiqueta ya dada de baja").
    Devuelve True si lo encontró y clicó.
    """
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


def ejecutar_baja_excel(xl, codigo: str, estado: str) -> bool:
    """
    Llama al macro DAR_DE_BAJA y gestiona el flujo de dos pasos:
      1. InputBox → activa la ventana del diálogo, luego envía el código + Enter
      2. UserForm de STATUS → localiza el botón 'DAR DE BAJA' por hwnd y hace BM_CLICK
    """
    import threading
    import win32com.client

    shell = win32com.client.Dispatch("WScript.Shell")
    opcion = MAPEO_ESTADO.get(estado, 1)

    def _enviar_secuencia():
        # ── Paso 1: InputBox ─────────────────────────────────────────────────
        # Buscamos la ventana del InputBox por su título y la ponemos en foco
        hwnd = _activar_dialogo_excel("ETIQUETA", timeout=4.0)
        if not hwnd:
            # Fallback: esperar y confiar en que Excel tenga foco
            time.sleep(0.8)
        shell.SendKeys("^a" + codigo + "~", 0)  # ^a = Ctrl+A para borrar texto previo

        # ── Paso 2: UserForm ──────────────────────────────────────────────────
        if opcion == 2:
            # Necesitamos bajar al segundo ítem del listbox
            time.sleep(1.0)
            # Buscar el listbox y seleccionar el segundo ítem via hwnd
            import win32gui, win32con
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

        # Clicar el botón DAR DE BAJA directamente via hwnd (sin necesitar foco)
        ok = _click_boton_dar_de_baja(timeout=6.0)
        if not ok:
            shell.SendKeys("{ENTER}", 0)

        # ── Paso 3: MsgBox de Excel ("Etiqueta ya dada de baja", "Aceptar", etc.)
        _click_boton_aceptar(timeout=8.0)

    t = threading.Thread(target=_enviar_secuencia, daemon=True)
    t.start()

    try:
        xl.Application.Run("DAR_DE_BAJA")
        return True
    except Exception as e:
        err = str(e)
        if "-2146788248" in err:
            print(f"  [i] Código no encontrado en Excel — marcando como procesado.")
            return True
        print(f"  [!] Error al ejecutar macro: {e}")
        return False


def _copiar_portapapeles(texto: str):
    """Copia texto al portapapeles de Windows con reintentos si está bloqueado."""
    import win32clipboard
    for _ in range(10):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(str(texto), win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except Exception:
                pass
            time.sleep(0.1)


def _hilo_semi_auto(codigo, parar_event):
    """
    Secuencia de teclado completa en el formulario MERAK KB:
      Foco inicial: botón SALIR
      TAB TAB       → campo Edit
      {codigo}      → escribir código
      TAB           → botón DAR DE BAJA
      ENTER         → ejecutar → aparece MsgBox
      ENTER         → cerrar MsgBox → foco vuelve al form
      TAB ENTER     → SALIR → cierra form → termina macro
    """
    import pythoncom
    import win32gui
    import win32com.client

    pythoncom.CoInitialize()
    try:
        shell = win32com.client.Dispatch("WScript.Shell")

        # ── Esperar a que aparezca MERAK KB ──────────────────────────────────
        deadline = time.time() + 15.0
        hwnd = None
        while not parar_event.is_set() and time.time() < deadline:
            hwnd = win32gui.FindWindow(None, "MERAK KB")
            if hwnd and win32gui.IsWindowVisible(hwnd):
                break
            time.sleep(0.15)

        if not hwnd or parar_event.is_set():
            return

        # Traer el formulario al frente
        try:
            win32gui.ShowWindow(hwnd, 9)       # SW_RESTORE por si está minimizado
            win32gui.SetForegroundWindow(hwnd)
        except Exception:
            pass
        time.sleep(0.4)

        # ── Paso 1: navegar al Edit y escribir el código ──────────────────────
        shell.SendKeys("{TAB}{TAB}", 0)
        time.sleep(0.15)
        shell.SendKeys(str(codigo), 0)
        time.sleep(0.15)

        # ── Paso 2: ir a DAR DE BAJA y pulsarlo ──────────────────────────────
        shell.SendKeys("{TAB}{ENTER}", 0)

        # ── Paso 3: esperar MsgBox y aceptarlo ───────────────────────────────
        CLASES_MAIN = {'XLMAIN', 'XLDESK', 'EXCEL7'}

        def _hijos_textos(h):
            textos = set()
            def cb(c, _):
                try:
                    t = win32gui.GetWindowText(c).strip().upper()
                    if t: textos.add(t)
                except Exception: pass
            try: win32gui.EnumChildWindows(h, cb, None)
            except Exception: pass
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
                except Exception: pass
            win32gui.EnumWindows(_check, None)

        time.sleep(0.1)
        shell.SendKeys("{ENTER}", 0)   # cerrar MsgBox
        time.sleep(0.5)

        # ── Paso 4: TAB → SALIR, ENTER → cerrar formulario ───────────────────
        shell.SendKeys("{TAB}{ENTER}", 0)

    finally:
        pythoncom.CoUninitialize()


def modo_semi_automatico(pendientes, xl):
    """
    Modo automático por secuencia de teclado.
    - Ítem 1: MANUAL — el script lanza la macro y espera a que tú hagas
      DAR DE BAJA → Aceptar → SALIR. Esto pone Excel en primer plano.
    - Ítems 2+: AUTOMÁTICO — el hilo envía la secuencia de teclado completa.
    """
    import threading

    total = len(pendientes)
    procesados = 0
    errores = 0

    print(f"\n  MODO AUTOMÁTICO")
    print(f"  El primer código lo gestionas TÚ para poner el formulario en primer plano.")
    print(f"  Del segundo en adelante el script lo hace solo.")
    print(f"\n  Procesando {total} baja(s)...\n")

    for i, m in enumerate(pendientes, 1):
        desc = (m['descripcion'] or 'Sin descripción')[:40]
        print(f"  [{i}/{total}] {m['codigo']}  ({m['estado']})  {desc}")

        _copiar_portapapeles(m['codigo'])
        parar = threading.Event()

        if i == 1:
            # ── Primer ítem: manual ──────────────────────────────────────────
            print(f"\n  ╔══════════════════════════════════════════════════════╗")
            print(f"  ║  ACCIÓN MANUAL REQUERIDA — solo esta vez             ║")
            print(f"  ╠══════════════════════════════════════════════════════╣")
            print(f"  ║  Código a procesar: {m['codigo']:<33}║")
            print(f"  ║                                                      ║")
            print(f"  ║  1. Pulsa el botón  DAR DE BAJA  del formulario      ║")
            print(f"  ║  2. Sitúate en el campo de texto del formulario      ║")
            print(f"  ║  3. Pega el código con  Ctrl+V  (ya está copiado)    ║")
            print(f"  ║  4. Pulsa el botón  DAR DE BAJA                      ║")
            print(f"  ║  5. Acepta el mensaje que aparece                    ║")
            print(f"  ║  6. Pulsa  SALIR  — el modo automático arrancará     ║")
            print(f"  ╚══════════════════════════════════════════════════════╝\n")
        else:
            # ── Ítems siguientes: automático ─────────────────────────────────
            hilo = threading.Thread(target=_hilo_semi_auto, args=(m['codigo'], parar,), daemon=True)
            hilo.start()

        try:
            xl.Application.Run("DAR_DE_BAJA")
            marcar_procesado(m['id'])
            procesados += 1
            print(f"         ✓ Procesado.")
        except Exception as e:
            err = str(e)
            if "-2146788248" in err:
                print(f"         [i] Código no encontrado en Excel — marcando como procesado.")
                marcar_procesado(m['id'])
                procesados += 1
            else:
                errores += 1
                print(f"         ✗ Error: {e}")
        finally:
            parar.set()

    print(f"\n{'─'*60}")
    print(f"  Procesados: {procesados} / {total}   Errores: {errores}")
    print(f"{'─'*60}\n")


def mostrar_lista(pendientes):
    print(f"\n{'─'*60}")
    print(f"  BAJAS PENDIENTES DE PROCESAR EN EXCEL ({len(pendientes)})")
    print(f"{'─'*60}")
    if not pendientes:
        print("  No hay bajas pendientes.")
    for i, m in enumerate(pendientes, 1):
        desc = (m['descripcion'] or 'Sin descripción')[:35]
        op = m['operario_numero'] or '---'
        print(f"  {i:>3}. [{m['estado'].upper():>8}] {m['codigo']}  {desc:<35}  Op: {op}")
    print(f"{'─'*60}\n")


def modo_automatico(pendientes, xl, confirmar_cada_uno=False):
    total = len(pendientes)
    procesados = 0
    errores = 0

    print(f"\nProcesando {total} baja(s) en Excel...\n")

    for i, m in enumerate(pendientes, 1):
        desc = (m['descripcion'] or 'Sin descripción')[:40]
        print(f"  [{i}/{total}] {m['codigo']}  ({m['estado']})  {desc}")

        if confirmar_cada_uno:
            resp = input("         ¿Procesar? [Enter=sí / s=saltar / q=salir] ").strip().lower()
            if resp == 'q':
                print("\n  Interrumpido por el usuario.")
                break
            if resp == 's':
                print("         → Saltado.")
                continue

        ok = ejecutar_baja_excel(xl, m['codigo'], m['estado'])
        if ok:
            marcar_procesado(m['id'])
            procesados += 1
            print(f"         ✓ Procesado.")
        else:
            errores += 1
            print(f"         ✗ Error — no marcado como procesado.")

        if i < total:
            time.sleep(PAUSA_ENTRE_BAJAS)

    print(f"\n{'─'*60}")
    print(f"  Procesados: {procesados} / {total}   Errores: {errores}")
    print(f"{'─'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Automatiza bajas en Excel vía macro DAR_DE_BAJA")
    parser.add_argument("--lista", action="store_true", help="Solo muestra los pendientes, sin procesar")
    parser.add_argument("--uno", action="store_true", help="Confirmar cada baja antes de ejecutar (automatico)")
    parser.add_argument("--semi", action="store_true", help="Semi-automatico: copia codigo al portapapeles, tu haces los clics")
    args = parser.parse_args()

    print("=" * 60)
    print("  BAJAS EXCEL — Gestión de Materiales")
    print("=" * 60)

    pendientes = get_pendientes()

    if args.lista:
        mostrar_lista(pendientes)
        return

    mostrar_lista(pendientes)

    if not pendientes:
        return

    xl = get_excel_instance()

    # Comprobar que Excel no está en modo edición
    if xl.Interactive is False:
        print("[AVISO] Excel está ocupado. Espera a que termine la operación actual.")
        sys.exit(1)

    if args.semi:
        modo_semi_automatico(pendientes, xl)
    else:
        modo_automatico(pendientes, xl, confirmar_cada_uno=args.uno)


if __name__ == "__main__":
    main()
