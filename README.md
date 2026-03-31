# Gestión de Materiales

Aplicación web en Flask para el control de materiales con códigos de barras, gestión de operarios y exportación a Excel.

## Características

- Registro y seguimiento de materiales con código EAN
- Generación de códigos de barras
- Control de estados: disponible, en uso, gastado, retirado, caducado…
- Sistema de roles: administrador, almacenero, operario
- Exportación a Excel
- Interfaz web responsive (también funciona desde móvil)
- Actualización automática desde GitHub (panel de administración)

## Requisitos

- **Python 3.10+** — [descargar](https://www.python.org/downloads/)
- **Git** — [descargar](https://git-scm.com/downloads)

## Instalación en un PC nuevo

```bash
git clone https://github.com/victorestebanmartin-design/GestionMateriales.git
cd GestionMateriales
python install.py
```

El instalador crea el entorno virtual, instala dependencias, inicializa las bases de datos y genera el script de arranque.

## Arranque

**Windows** (doble clic o desde terminal):
```
start.bat
```

**Manual** (cualquier SO):
```bash
.venv\Scripts\python run_app_window.py   # Windows
.venv/bin/python run_app_window.py       # Linux / macOS
```

La app abre en ventana nativa. Acceso también desde cualquier PC de la red en `http://<IP-del-servidor>:5000`.

## Actualización automática

1. Entra en `/admin` con tu cuenta de administrador.
2. Baja hasta la sección **"🔄 Actualización de la aplicación"**.
3. Pulsa **"Actualizar desde GitHub"** — ejecuta `git pull` + `pip install`.
4. Si hubo cambios, aparece el botón **"♻️ Reiniciar aplicación"**.

O manualmente desde terminal:
```bash
git pull origin main
.venv\Scripts\pip install -r requirements.txt
```

## Credenciales por defecto

| Número | Rol |
|--------|-----|
| `999999` | Administrador |
| `US4281` | Administrador |
| `US272` | Almacenero |
| `US25013` | Almacenero |

Las contraseñas/PINs se configuran con variables de entorno o directamente en `app.py`:
```
ADMIN_PASSWORD, ALMACEN_PIN, OPERARIO_PIN
```

## Estructura del proyecto

```
GestionMateriales/
├── app.py                    # Aplicación principal (Flask)
├── run_app_window.py         # Arranque en ventana nativa (pywebview)
├── install.py                # Instalador cross-platform
├── start.bat                 # Arranque rápido Windows
├── requirements.txt          # Dependencias Python
├── crear_icono.py            # Generador de iconos PWA
├── LibreBarcode128-Regular.ttf
├── database/
│   ├── create_herramientas_db.py   # Crea las BD en el primer uso
│   ├── materiales.db               # [NO en Git – datos locales]
│   └── operarios.db                # [NO en Git – datos locales]
├── shared/
│   ├── auth.py
│   └── operarios_db.py
└── static/icons/
```

## Bases de datos

Los archivos `.db` no se suben a GitHub (están en `.gitignore`). Para copiar datos entre equipos, copia manualmente `database/materiales.db` y `database/operarios.db`.

## Tecnologías

- **Backend**: Flask + Werkzeug
- **Frontend**: HTML5 / CSS3 / JavaScript (sin frameworks)
- **BD**: SQLite
- **Códigos de barras**: python-barcode + Pillow
- **Excel**: openpyxl
- **Ventana nativa**: pywebview
