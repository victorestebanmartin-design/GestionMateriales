#!/usr/bin/env python3
"""
Agente cliente para procesar bajas en Excel desde el PC que tiene Excel abierto.

Este script corre en el PC que tiene acceso al archivo Excel (NO en el servidor).
Consulta el servidor cada pocos segundos y, cuando el admin pulsa el botón
"📡 Enviar al PC cliente" en el panel de administración, ejecuta la automatización
de Excel localmente y reporta el resultado al servidor.

Uso:
    python baja_excel_agente.py
    python baja_excel_agente.py --servidor http://192.168.1.10:5000 --token admin123

Configuración rápida: edita las constantes SERVER_URL y AGENT_TOKEN en este archivo.
"""

import sys
import os
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Configuración ─────────────────────────────────────────────────────────────
# Cambia estos valores antes de ejecutar, o pásalos como argumentos
SERVER_URL  = "http://192.168.1.10:5000"  # URL del servidor Flask
AGENT_TOKEN = "admin123"                   # Contraseña del administrador
POLL_INTERVAL = 5                          # Segundos entre comprobaciones
# ──────────────────────────────────────────────────────────────────────────────

try:
    import requests
except ImportError:
    print("[ERROR] El paquete 'requests' no está instalado.")
    print("        Ejecuta:  .venv\\Scripts\\pip install requests")
    sys.exit(1)

# Importar funciones de automatización de Excel desde baja_excel.py
try:
    from baja_excel import get_excel_instance, ejecutar_baja_excel, PAUSA_ENTRE_BAJAS
except ImportError as e:
    print(f"[ERROR] No se pudo importar baja_excel.py: {e}")
    print("        Asegúrate de ejecutar este script desde la carpeta GestionMateriales.")
    sys.exit(1)


def _headers():
    return {"Authorization": f"Bearer {AGENT_TOKEN}"}


def _poll():
    """Consulta si hay una solicitud pendiente. Actualiza el timestamp online."""
    r = requests.get(f"{SERVER_URL}/api/agente/poll", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("hay_solicitud", False)


def _get_pendientes():
    r = requests.get(f"{SERVER_URL}/api/agente/pendientes", headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json().get("pendientes", [])


def _marcar_iniciando():
    requests.post(f"{SERVER_URL}/api/agente/iniciar", headers=_headers(), timeout=10)


def _reportar_completado(procesados, errores, salida, ids_ok):
    requests.post(
        f"{SERVER_URL}/api/agente/completar",
        headers=_headers(),
        json={"procesados": procesados, "errores": errores,
              "salida": salida, "ids_procesados": ids_ok},
        timeout=30,
    )


def _reportar_error(mensaje):
    requests.post(
        f"{SERVER_URL}/api/agente/error",
        headers=_headers(),
        json={"mensaje": mensaje},
        timeout=10,
    )


def procesar():
    """Descarga pendientes, ejecuta la macro en Excel y reporta al servidor."""
    pendientes = _get_pendientes()
    if not pendientes:
        _reportar_completado(0, 0, "No habia pendientes.", [])
        return

    xl = get_excel_instance()

    if xl.Interactive is False:
        raise RuntimeError("Excel está ocupado. Espera a que termine la operación actual.")

    total = len(pendientes)
    procesados = 0
    errores = 0
    ids_ok = []
    lineas = [f"Procesando {total} baja(s)...", ""]

    for i, m in enumerate(pendientes, 1):
        desc = (m.get("descripcion") or "Sin descripcion")[:40]
        lineas.append(f"[{i}/{total}] {m['codigo']}  {desc}")
        try:
            ok = ejecutar_baja_excel(xl, m["codigo"], m["estado"])
            if ok:
                ids_ok.append(m["id"])
                procesados += 1
                lineas.append("  -> OK")
            else:
                errores += 1
                lineas.append("  -> ERROR (macro devolvio False)")
        except Exception as e:
            errores += 1
            lineas.append(f"  -> ERROR: {e}")

        if i < total:
            time.sleep(PAUSA_ENTRE_BAJAS)

    lineas.append("")
    lineas.append(f"Procesados: {procesados}/{total}   Errores: {errores}")
    salida = "\n".join(lineas)
    _reportar_completado(procesados, errores, salida, ids_ok)
    return procesados, errores


def main():
    global SERVER_URL, AGENT_TOKEN

    parser = argparse.ArgumentParser(
        description="Agente cliente para procesar bajas en Excel desde este PC"
    )
    parser.add_argument(
        "--servidor",
        default=SERVER_URL,
        help=f"URL del servidor Flask (ej: http://192.168.1.10:5000). Default: {SERVER_URL}",
    )
    parser.add_argument(
        "--token",
        default=AGENT_TOKEN,
        help="Contraseña del administrador (usada como token Bearer)",
    )
    args = parser.parse_args()
    SERVER_URL  = args.servidor.rstrip("/")
    AGENT_TOKEN = args.token

    print("=" * 60)
    print("  AGENTE BAJAS EXCEL — Gestor de Materiales")
    print("=" * 60)
    print(f"  Servidor : {SERVER_URL}")
    print(f"  Intervalo: {POLL_INTERVAL} s")
    print("  Esperando solicitudes del admin... (Ctrl+C para salir)")
    print()

    while True:
        try:
            hay_solicitud = _poll()
            if hay_solicitud:
                ts = time.strftime("%H:%M:%S")
                print(f"[{ts}] Solicitud recibida. Iniciando proceso...")
                _marcar_iniciando()
                try:
                    procesar()
                    print(f"[{ts}] Proceso completado. Resultado enviado al servidor.")
                except Exception as e:
                    print(f"[{ts}] ERROR durante el proceso: {e}")
                    _reportar_error(str(e))
        except requests.exceptions.ConnectionError:
            print(f"[{time.strftime('%H:%M:%S')}] Sin conexion al servidor, reintentando...")
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] Error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
