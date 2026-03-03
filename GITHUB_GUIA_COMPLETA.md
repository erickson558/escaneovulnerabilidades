# Cómo Subir Escaneovulnerabilidades a GitHub

## 🚀 Resumen Rápido

Este documento contiene los comandos exactos para subir tu proyecto a GitHub.

---

## Paso 1: Crear Repositorio en GitHub

### En la navegador web:

1. Ve a: **https://github.com/new**
2. Completa el formulario:
   - **Repository name:** `escaneovulnerabilidades`
   - **Description:** `Professional system vulnerability scanner`
   - **Public:** ✅ (marca la opción)
   - **Initialize this repository:** ❌ (NO marcar)

3. Click en **"Create repository"**

---

## Paso 2: Copiar URL del Repositorio

Después de crear, GitHub te mostrará una pantalla con:

```
https://github.com/TU_USUARIO/escaneovulnerabilidades.git
```

**Copia esta URL** (la necesitarás en el siguiente paso)

---

## Paso 3: Ejecutar Comandos en PowerShell

Abre PowerShell en la carpeta del proyecto y ejecuta estos comandos en orden:

### 3.1 Navegar a la carpeta
```powershell
cd "d:\OneDrive\Regional\1 pendientes para analisis\proyectospython\escaneovulnerabilidades"
```

### 3.2 Verificar que Git está inicializado
```powershell
git status
```

Deberías ver:
```
On branch master
...
```

### 3.3 Cambiar rama a "main"
```powershell
git branch -M main
```

### 3.4 Agregar repositorio remoto

**REEMPLAZA `TU_USUARIO` con tu usuario de GitHub:**

```powershell
git remote add origin https://github.com/TU_USUARIO/escaneovulnerabilidades.git
```

**Ejemplo:**
```powershell
git remote add origin https://github.com/juanperez/escaneovulnerabilidades.git
```

### 3.5 Verificar conexión
```powershell
git remote -v
```

Deberías ver:
```
origin  https://github.com/TU_USUARIO/escaneovulnerabilidades.git (fetch)
origin  https://github.com/TU_USUARIO/escaneovulnerabilidades.git (push)
```

### 3.6 Subir cambios a GitHub

```powershell
git push -u origin main
```

**¿Pide contraseña?**

GitHub no acepta contraseña directa. Usa un **Personal Access Token**:

1. Ve a: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Dale nombre: `escaneovulnerabilidades`
4. Selecciona: ✅ **repo** (full control)
5. Click **"Generate token"**
6. **COPIA el token** (no lo pierdas)
7. Cuando te pida contraseña, pega el token

---

## Paso 4: Verificar Upload en GitHub

Ve a: **https://github.com/TU_USUARIO/escaneovulnerabilidades**

Deberías ver todos tus archivos en la rama `main` ✅

---

## Paso 5: Crear Versión (Release) v2.0.0

### Opción A: Desde Terminal (más rápido)

```powershell
# Crear tag local
git tag v2.0.0

# Subir tag a GitHub
git push origin v2.0.0
```

### Opción B: Desde GitHub Web

1. Ve a tu repositorio
2. Click en **"Releases"** (lateral derecho)
3. Click **"Draft a new release"**
4. **Tag version:** `v2.0.0`
5. **Release title:** `v2.0.0 - Refactorización Completa`
6. **Description:** (pega esto)

```
## Cambios principales v2.0.0

### ✨ Mejoras
- ✅ Refactorización completa con arquitectura modular
- ✅ Separación backend/frontend en módulos independientes
- ✅ Implementación de type hints en todas funciones
- ✅ Docstrings completos (estándar Google)
- ✅ Sistema de logging estructurado (LoggerManager)
- ✅ Gestor de configuración centralizado (ConfigManager)
- ✅ Clase VulnerabilityScanner refactorizada
- ✅ Generador de PDF profesional (PDFReportGenerator)
- ✅ Interfaz gráfica mejorada y responsive

### 📦 Compilación
- Ejecutable generado con icono personalizado
- PyInstaller optimizado
- Binario listo en `dist/`

### 📚 Documentación
- README completo
- Licencia Apache 2.0
- Guía Git paso a paso
- requirements.txt actualizado
- Workflow GitHub Actions para releases automáticos

### 🔄 Compatibilidad
- Python 3.8+
- Windows, Linux, macOS
- SIN cambios en funcionalidad original
- 100% compatible con versiones anteriores
```

7. Click **"Publish release"**

---

## Paso 6: Verificar Release en GitHub

Ve a tu repositorio → **Releases**

Deberías ver tu versión `v2.0.0` listada ✅

---

## Paso 7: Configurar Workflow Automático

El workflow para releases automáticos **YA ESTÁ CONFIGURADO** en `.github/workflows/release.yml`

Esto significa que cada vez que hagas push a `main`, se creará automáticamente un release.

Para verificar:
1. Ve a tu repositorio
2. Click en **"Actions"**
3. Deberías ver el workflow **"Release"**

---

## 📋 Flujo Completo de Comandos

Aquí están TODOS los comandos ejecutados juntos:

```powershell
# 1. Navegar
cd "d:\OneDrive\Regional\1 pendientes para analisis\proyectospython\escaneovulnerabilidades"

# 2. Cambiar rama a main
git branch -M main

# 3. Agregar repositorio remoto (REEMPLAZA TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/escaneovulnerabilidades.git

# 4. Subir a GitHub
git push -u origin main

# 5. Crear versión
git tag v2.0.0
git push origin v2.0.0

# 6. Verificar
git remote -v
git tag -l
git log --oneline -5
```

---

## 🔑 Gestionar Tokens de GitHub

### Ver tokens creados:
https://github.com/settings/tokens

### Revocar token:
1. Ve a https://github.com/settings/tokens
2. Encuentra el token `escaneovulnerabilidades`
3. Click **"Delete"**

### Cambiar credenciales guardadas en Windows:
1. **Búsqueda Windows:** "Administrador de credenciales"
2. Click en **"Credenciales de Windows"**
3. Busca `github.com`
4. Click **"Editar"** y actualiza el token

---

## ✅ Checklist de Verificación

Después de completar todos los pasos:

- [ ] Repositorio visible en GitHub
- [ ] Todos los archivos presentes en rama `main`
- [ ] Rama `main` es la rama por defecto
- [ ] Release `v2.0.0` creada
- [ ] Workflow "Release" visible en Actions
- [ ] README visible en página principal
- [ ] LICENSE visible
- [ ] requirements.txt accesible
- [ ] Ejecutable en `dist/` compilado

---

## 🐛 Solución de Problemas

### Error: "fatal: remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/escaneovulnerabilidades.git
```

### Error: "Permission denied"

Usa un **Personal Access Token** en lugar de contraseña.

### Error: "Repository not found"

- Verifica que el nombre sea exacto: `escaneovulnerabilidades`
- Verifica que el repositorio sea **Public**
- Verifica la URL correcta

### Cambios no aparecen en GitHub

```powershell
git push origin main
```

---

## 📚 Próximos Pasos

### Actualizar versión en futuro:

```powershell
# 1. Editar src/__init__.py
#    Cambiar: __version__ = "2.0.1"

# 2. Commit
git add src/__init__.py
git commit -m "bump: versión a 2.0.1"

# 3. Tag
git tag v2.0.1
git push origin main v2.0.1

# ✅ Release se crea automáticamente!
```

### Clonar desde GitHub:

```powershell
git clone https://github.com/TU_USUARIO/escaneovulnerabilidades.git
cd escaneovulnerabilidades
pip install -r requirements.txt
python main.py
```

---

## 🎉 ¡Listo!

Tu proyecto está en GitHub con:
- ✅ Repositorio público
- ✅ Documentación completa
- ✅ Licencia Apache 2.0
- ✅ Versionamiento semántico
- ✅ Releases automáticas
- ✅ Historial de commits

**¡Felicidades! Ahora eres un desarrollador con mejor versionamiento.** 🚀

---

**Preguntas?** Consulta:
- https://docs.github.com/
- https://git-scm.com/book
- https://www.conventionalcommits.org/
