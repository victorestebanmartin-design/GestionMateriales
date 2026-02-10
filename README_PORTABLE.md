# 📱 GESTIÓN DE MATERIALES - VERSIÓN PORTABLE

Una aplicación completa para gestión de materiales que funciona **SIN internet** y **SIN instalar Python**.

## 🎯 Características de la Versión Portable

- ✅ **Completamente OFFLINE** - No requiere conexión a internet
- ✅ **Sin instalación de Python** - Incluye Python embebido
- ✅ **Acceso en red local** - Otros PCs pueden conectarse
- ✅ **Exportación Excel offline** - Funciona sin conexión
- ✅ **Base de datos incluida** - SQLite integrado
- ✅ **Interfaz web moderna** - Acceso desde cualquier navegador

## 🚀 PREPARACIÓN (PC con internet)

### Paso 1: Descargar Python Portable
```cmd
descargar_python_portable.bat
```
Este script descarga Python embebido (~15 MB) desde python.org

### Paso 2: Preparar Paquete Completo
```cmd
preparar_paquete_completo.bat
```
Este script:
- Instala dependencias en Python portable
- Crea estructura portable completa
- Genera scripts de ejecución
- **Resultado**: Carpeta `GestionMateriales_Portable/` (~50-70 MB)

## 💾 INSTALACIÓN (PC sin internet/Python)

### 1. Copiar Archivos
- Copie toda la carpeta `GestionMateriales_Portable/` al PC destino
- Ubicación sugerida: `C:\GestionMateriales\` o escritorio

### 2. Ejecutar Aplicación
Doble clic en: **`INICIAR_APP.bat`**

La aplicación:
- ✅ Se abre automáticamente en el navegador
- ✅ Muestra las direcciones de acceso disponibles
- ✅ Funciona inmediatamente sin configuración

### 3. Configurar Red (Opcional)
Si necesita acceso desde otros PCs:
1. Clic derecho en `CONFIGURAR_RED.bat`
2. Seleccionar **"Ejecutar como administrador"**
3. Confirmar configuración del firewall

## 🌐 Acceso a la Aplicación

### Acceso Local
```
http://localhost:5000
```

### Acceso desde Red
```
http://[IP-DEL-PC]:5000
```
*La IP se muestra automáticamente al iniciar*

### Credenciales Administrador
- **Usuario**: `999`
- **PIN**: *(dejar en blanco)*

## 📊 Funcionalidades Disponibles

### ✅ Gestión Completa OFFLINE
- Registro y control de materiales
- Movimientos de entrada y salida
- Consultas y reportes
- Panel de administración

### ✅ Importación/Exportación Excel
- Funciona completamente offline
- No requiere Microsoft Office
- Formatos compatibles: .xlsx, .xls

### ✅ Multi-usuario en Red
- Acceso simultáneo desde múltiples PCs
- Base de datos centralizada
- Actualizaciones en tiempo real

## 🔧 Requisitos del PC Destino

### Mínimos
- **Sistema**: Windows 7/8/10/11 (32 o 64 bits)
- **RAM**: 2 GB mínimo
- **Espacio**: 100 MB libres
- **Navegador**: Internet Explorer 11+ / Chrome / Firefox / Edge

### Recomendados
- **RAM**: 4 GB o más
- **Espacio**: 500 MB libres
- **Navegador**: Chrome o Edge (mejor rendimiento)

## 🗂️ Estructura del Paquete Portable

```
GestionMateriales_Portable/
├── 🚀 INICIAR_APP.bat          # Ejecutar aplicación
├── 🌐 CONFIGURAR_RED.bat       # Configurar acceso en red
├── 📱 app.py                   # Aplicación principal
├── 📋 requirements.txt         # Dependencias (referencia)
├── 🐍 python/                  # Python embebido
│   ├── python.exe             # Ejecutable Python
│   ├── Lib/                   # Librerías Python
│   └── Scripts/               # Scripts adicionales
└── 📊 database/               # Base de datos
    ├── materiales.db          # Base materiales
    └── operarios.db           # Base operarios
```

## 🆘 Solución de Problemas

### La aplicación no inicia
1. ✅ Verificar que existe `python/python.exe`
2. ✅ Comprobar permisos de ejecución
3. ✅ Ejecutar como administrador si es necesario

### No se abre el navegador
1. ✅ Abrir manualmente: `http://localhost:5000`
2. ✅ Verificar que no hay otro programa en puerto 5000
3. ✅ Revisar firewall de Windows

### No funciona en red
1. ✅ Ejecutar `CONFIGURAR_RED.bat` como administrador
2. ✅ Verificar IP mostrada en pantalla
3. ✅ Comprobar que ambos PCs están en la misma red

### Error de permisos
1. ✅ Copiar carpeta a una ubicación con permisos (ej: Documentos)
2. ✅ Ejecutar scripts como administrador
3. ✅ Desactivar temporalmente antivirus

## 📞 Información Técnica

- **Versión**: 2.0 Portable
- **Framework**: Flask 3.1.2
- **Base de datos**: SQLite
- **Compatibilidad**: Windows 7+ (32/64 bits)
- **Tamaño**: ~50-70 MB completo
- **Python**: 3.13 embebido

## 🎉 ¡Listo para Usar!

La aplicación está completamente preparada para funcionar en cualquier PC Windows sin requerir instalaciones adicionales. Solo copie, ejecute y use.

---
*Versión Portable - Gestión de Materiales v2.0*