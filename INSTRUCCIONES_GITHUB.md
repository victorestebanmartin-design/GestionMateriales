# 📝 Instrucciones para subir a GitHub y trabajar desde múltiples PCs

## ✅ Paso 1: Crear el repositorio en GitHub (Ya completado localmente)

El repositorio Git ya está inicializado localmente y el primer commit está hecho. ✨

## 🌐 Paso 2: Crear el repositorio en GitHub.com

1. Ve a [GitHub.com](https://github.com)
2. Haz clic en el botón **"+"** en la esquina superior derecha
3. Selecciona **"New repository"**
4. Llena los siguientes campos:
   - **Repository name**: `GestionMateriales` (o el nombre que prefieras)
   - **Description**: "Sistema de Gestión de Materiales con Flask"
   - **Public/Private**: Elige según tus necesidades
   - ⚠️ **NO marques** "Initialize this repository with a README" (ya tenemos uno)
5. Haz clic en **"Create repository"**

## 🔗 Paso 3: Conectar tu repositorio local con GitHub

Después de crear el repositorio en GitHub, verás una página con instrucciones. 
Ejecuta estos comandos en tu terminal (PowerShell):

```powershell
# Configurar tu información de Git (solo primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"

# Agregar el repositorio remoto (sustituye TU_USUARIO por tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/GestionMateriales.git

# Subir el código a GitHub
git branch -M main
git push -u origin main
```

⚠️ **Importante**: Reemplaza `TU_USUARIO` con tu nombre de usuario de GitHub.

## 💻 Paso 4: Clonar en otro PC

En el segundo PC, ejecuta:

```powershell
# Navegar a donde quieres guardar el proyecto
cd C:\Users\TU_USUARIO\Desktop

# Clonar el repositorio
git clone https://github.com/TU_USUARIO/GestionMateriales.git
cd GestionMateriales

# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Crear las bases de datos (primera vez)
python database\create_herramientas_db.py

# Ejecutar la aplicación
python app.py
```

## 🔄 Paso 5: Flujo de trabajo con múltiples PCs

### 📤 Cuando termines de trabajar en un PC:

```powershell
# Ver qué cambios hiciste
git status

# Agregar todos los cambios
git add .

# Hacer commit con un mensaje descriptivo
git commit -m "Descripción de tus cambios"

# Subir los cambios a GitHub
git push
```

### 📥 Antes de empezar a trabajar en otro PC:

```powershell
# Descargar los últimos cambios
git pull

# Si hay nuevas dependencias en requirements.txt
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## ⚠️ Notas importantes

1. **Bases de datos**: Los archivos `.db` NO se sincronizan en Git (están en .gitignore por seguridad)
   - Si necesitas la misma base de datos en ambos PCs, cópiala manualmente
   - O trabaja con bases de datos diferentes en cada PC

2. **Entorno virtual**: Cada PC debe tener su propio `.venv` (no se sube a Git)

3. **Conflictos**: Si dos personas editan el mismo archivo:
   ```powershell
   # Git te avisará del conflicto al hacer pull
   git pull
   # Edita los archivos marcados con conflictos
   # Luego:
   git add .
   git commit -m "Resuelto conflicto"
   git push
   ```

4. **Autenticación con GitHub**: La primera vez que hagas `push`, GitHub te pedirá autenticación:
   - Usa un **Personal Access Token** (PAT) en lugar de contraseña
   - Generarlo en: GitHub → Settings → Developer settings → Personal access tokens

## 🎯 Comandos útiles

```powershell
# Ver el historial de cambios
git log --oneline

# Ver cambios sin confirmar
git diff

# Descartar cambios locales (cuidado!)
git checkout -- archivo.py

# Ver repositorios remotos configurados
git remote -v

# Ver rama actual
git branch
```

## ✨ ¡Todo listo!

Ahora puedes trabajar desde cualquier PC y mantener tu código sincronizado con GitHub.
