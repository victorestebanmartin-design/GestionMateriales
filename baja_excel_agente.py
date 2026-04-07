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
SERVER_URL  = "http://192.168.1.10:5000"  # URL del servidor Flask
AGENT_TOKEN = "admin123"                   # Contraseña del administrador
POLL_INTERVAL = 5                          # Segundos entre comprobaciones
# ──────────────────────────────────────────────────────────────────────────────

try:
    import requests
except ImportError:
    print("[ERROR] El paquete 'requests' no está instalado.")
    print("        Ejecuta:  pip install requests")
    sys.exit(1)

# Importar funciones de automatización de Excel desde baja_excel.py
try:
    from baja_excel import get_excel_instance, modo_semi_automatico, PAUSA_ENTRE_BAJAS
except ImportError as e:
    print(f"[ERROR] No se pudo importar baja_excel.py: {e}")
    print("        Asegúrate de ejecutar este script desde la carpeta que contiene baja_excel.py.")
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


def _esta_cancelado():
    """Comprueba si el admin ha detenido el proceso."""
    try:
        r = requests.get(f"{SERVER_URL}/api/agente/cancelado", headers=_headers(), timeout=5)
        return r.json().get("cancelado", False)
    except Exception:
        return False


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
    """
    Descarga pendientes del servidor, ejecuta modo_semi_automatico localmente
    (que usa _hilo_semi_auto para controlar MERAK KB) y reporta al servidor.
    """
    pendientes = _get_pendientes()
    if not pendientes:
        _reportar_completado(0, 0, "No habia pendientes.", [])
        return 0, 0

    xl = get_excel_instance()

    if xl.Interactive is False:
        raise RuntimeError("Excel está ocupado. Espera a que termine la operación actual.")

    # Envolver modo_semi_automatico para capturar progreso e ids procesados.
    # Como modo_semi_automatico llama internamente a marcar_procesado (BD local),
    # aquí le pasamos una versión que también acumula los ids para reportar al servidor.
    import threading
    from baja_excel import _hilo_semi_auto, _copiar_portapapeles, PAUSA_ENTRE_BAJAS

    total = len(pendientes)
    procesados = 0
    errores = 0
    ids_ok = []
    lineas = [f"Procesando {total} baja(s)...", ""]

    for i, m in enumerate(pendientes, 1):
        # Comprobar cancelación antes de cada baja
        if _esta_cancelado():
            lineas.append(f"[{i}/{total}] Proceso detenido por el admin.")
            break

        desc = (m.get("descripcion") or "Sin descripcion")[:40]
        lineas.append(f"[{i}/{total}] {m['codigo']}  {desc}")

        _copiar_portapapeles(m["codigo"])
        parar = threading.Event()
        hilo = threading.Thread(
            target=_hilo_semi_auto, args=(m["codigo"], parar), daemon=True
        )
        hilo.start()

        try:
            xl.Application.Run("DAR_DE_BAJA")
            ids_ok.append(m["id"])
            procesados += 1
            lineas.append("  -> OK")
        except Exception as e:
            err = str(e)
            if "-2146788248" in err:
                # Código no encontrado en el Excel — se considera procesado igualmente
                ids_ok.append(m["id"])
                procesados += 1
                lineas.append("  -> Código no encontrado en Excel (marcado como procesado)")
            else:
                errores += 1
                lineas.append(f"  -> ERROR: {e}")
        finally:
            parar.set()

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
        help="Contraseña del administrador o número de operario admin",
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
                    proc, err = procesar()
                    print(f"[{ts}] Completado: {proc} procesados, {err} errores.")
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
