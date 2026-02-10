# 🏗️ Sistema de Gestión de Materiales

Aplicación web para el control de materiales de construcción con gestión de inventario, códigos de barras y registro de operarios.

## 📋 Características

- ✅ Gestión de materiales con códigos de barras
- 📊 Control de stock y ubicaciones
- 👥 Sistema de autenticación de operarios
- 📈 Exportación a Excel
- 🖨️ Generación de códigos de barras
- 💻 Interfaz web responsive

## 🚀 Instalación

### Requisitos previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar y actualizar el repositorio)

### Instalación rápida

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/GestionMateriales.git
cd GestionMateriales

# Crear entorno virtual (recomendado)
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear la base de datos (primera vez solamente)
python database/create_herramientas_db.py

# Ejecutar la aplicación
python app.py
```

La aplicación estará disponible en: `http://localhost:5000`

### 🔄 Trabajar desde múltiples PCs

**En el primer PC (ya configurado):**
```bash
# Hacer push de tus cambios
git add .
git commit -m "Descripción de los cambios"
git push
```

**En otro PC (primera vez):**
```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/GestionMateriales.git
cd GestionMateriales

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar las bases de datos del PC original (si es necesario)
# O crear nuevas bases de datos
python database/create_herramientas_db.py
```

**Para actualizar en cualquier PC:**
```bash
# Obtener últimos cambios
git pull

# Si hay nuevas dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## 📦 Versión Portable

Para instalar en equipos sin internet:

```bash
# Ejecutar el instalador completo
instalar_completo.bat
```

Esto:
1. Descarga Python portable
2. Instala todas las dependencias
3. Crea un paquete portable listo para usar

## 🗄️ Base de Datos

Las bases de datos se crean automáticamente en la carpeta `database/`:
- `materiales.db` - Inventario de materiales
- `operarios.db` - Usuarios y autenticación

**⚠️ Importante**: Las bases de datos NO se sincronizan con Git por seguridad. Para migrar datos entre equipos:

```bash
# Copiar manualmente los archivos .db de un equipo a otro
database/materiales.db
database/operarios.db
```

## 🛠️ Tecnologías

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Base de datos**: SQLite
- **Códigos de barras**: python-barcode
- **Excel**: openpyxl

## 📱 Uso

1. **Login**: Accede con tu usuario y contraseña
2. **Registro de materiales**: Añade nuevos materiales al inventario
3. **Generación de códigos**: Crea códigos de barras para cada material
4. **Control de stock**: Actualiza entradas y salidas
5. **Reportes**: Exporta el inventario a Excel

## 🔐 Seguridad

- Las contraseñas se almacenan con hash
- Sesiones seguras con tokens
- Validación de formularios

## 📄 Licencia

Este proyecto es de uso interno.

## 👨‍💻 Autor

Desarrollado para gestión interna de materiales.
