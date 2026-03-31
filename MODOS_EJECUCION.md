# Modos de Ejecución de la Aplicación

La aplicación de Gestión de Materiales puede ejecutarse de **tres formas diferentes**:

## 🌐 Modo 1: Navegador Web (Original)
**Archivo:** `ejecutar_aplicacion.bat`

- ✅ Abre la aplicación en tu navegador predeterminado
- ✅ Muestra la barra de direcciones y controles del navegador
- ✅ Ideal para acceso desde múltiples dispositivos en red
- 👉 **Recomendado para:** Uso compartido en red

```bash
ejecutar_aplicacion.bat
```

---

## 🖥️ Modo 2: Ventana Nativa en Pantalla Completa
**Archivo:** `ejecutar_ventana_nativa.bat`

- ✅ Sin barra de navegador
- ✅ Pantalla completa automática
- ✅ Apariencia de aplicación de escritorio profesional
- ✅ Botones minimizar/cerrar disponibles
- 👉 **Recomendado para:** Uso principal en estación de trabajo

**Controles:**
- `F11`: Alternar pantalla completa
- `Alt+F4`: Cerrar aplicación
- `Esc`: Salir de pantalla completa

```bash
ejecutar_ventana_nativa.bat
```

---

## 🎨 Modo 3: Ventana Sin Bordes (Moderna)
**Archivo:** `ejecutar_ventana_sin_bordes.bat`

- ✅ Sin bordes de ventana
- ✅ Apariencia ultra moderna
- ✅ Ventana arrastrable desde cualquier parte
- ✅ Tamaño personalizable
- 👉 **Recomendado para:** Apariencia minimalista y moderna

**Controles:**
- **Arrastrar:** Clic y mantener en cualquier lugar de la ventana
- **Cerrar:** Ctrl+W o cerrar la consola
- **Redimensionar:** Desde las esquinas

```bash
ejecutar_ventana_sin_bordes.bat
```

---

## 📦 Requisitos Adicionales

Para los **modos 2 y 3**, se necesita la librería `pywebview`:

```bash
pip install pywebview
```

Esta librería se instalará automáticamente la primera vez que ejecutes cualquiera de los scripts de ventana nativa.

---

## 🔧 Instalación de Dependencias

Si aún no tienes todas las dependencias instaladas:

```bash
pip install -r requirements.txt
```

---

## 🎯 ¿Cuál elegir?

| Modo | Mejor para |
|------|-----------|
| **Navegador Web** | Acceso desde múltiples dispositivos, uso en red |
| **Ventana Pantalla Completa** | Uso dedicado en una estación, máxima inmersión |
| **Ventana Sin Bordes** | Apariencia moderna y minimalista, multitarea |

---

## 🔑 Acceso de Administrador

En todos los modos:
- **Usuario:** `999999`
- **Contraseña:** *(dejar en blanco)*

---

## 💡 Notas

- Todos los modos ejecutan la misma aplicación Flask
- Los datos se comparten entre todos los modos (misma base de datos)
- Puedes tener múltiples modos ejecutándose simultáneamente en diferentes dispositivos
- El servidor siempre está disponible en `http://localhost:5000`
