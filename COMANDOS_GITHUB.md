# 📋 COMANDOS PARA GITHUB - Copia y Pega

Este archivo contiene los **comandos exactos** que debes ejecutar para subir tu proyecto a GitHub.

**Copiar y pegar los comandos tal como están.**

---

## PASO 1: Crear Repositorio en GitHub (En navegador)

### Acciones manuales (no hay comandos aquí):

1. Abre: https://github.com/new
2. Llena el formulario:
   - **Repository name**: `escaneovulnerabilidades`
   - **Description**: `Professional system vulnerability scanner`
   - **Public**: ✅ Marca
   - **Initialize repository**: ❌ NO marques
3. Click **"Create repository"**

GitHub te mostrará una pantalla con url. Copia:
```
https://github.com/TU_USUARIO/escaneovulnerabilidades.git
```

**Nota:** Reemplaza `TU_USUARIO` con tu usuario de GitHub (ej: juanperez)

---

## PASO 2: Ejecutar Comandos en PowerShell

Abre **PowerShell** y copia-pega estos comandos **EN ORDEN UNO POR UNO**:

### 2.1 Navegar a carpeta
```powershell
cd "d:\OneDrive\Regional\1 pendientes para analisis\proyectospython\escaneovulnerabilidades"
```

### 2.2 Cambiar rama a main
```powershell
git branch -M main
```

### 2.3 Agregar repositorio remoto

**IMPORTANTE: Reemplaza `TU_USUARIO` antes de ejecutar**

```powershell
git remote add origin https://github.com/TU_USUARIO/escaneovulnerabilidades.git
```

**Ejemplo real:**
```powershell
git remote add origin https://github.com/juanperez/escaneovulnerabilidades.git
```

### 2.4 Subir cambios a GitHub
```powershell
git push -u origin main
```

**¿Pide contraseña?**

GitHub no acepta contraseña. Genera un **Personal Access Token**:

1. Ve a: https://github.com/settings/tokens
2. Click **"Generate new token (classic)"**
3. Nombre: `escaneovulnerabilidades`
4. Marca: ✅ **repo** (full control of repositories)
5. Click abajo: **"Generate token"**
6. **COPIA el token** (es una cadena larga)
7. Cuando PowerShell pida contraseña, **pega el token**

---

## PASO 3: Crear Versión (Release)

Ejecuta estos comandos en PowerShell:

### 3.1 Crear tag local
```powershell
git tag v2.0.0
```

### 3.2 Subir tag a GitHub
```powershell
git push origin v2.0.0
```

**Resultado:** GitHub Actions creará el release automáticamente ✅

---

## PASO 4: Verificar (En navegador)

1. Ve a: `https://github.com/TU_USUARIO/escaneovulnerabilidades`
2. Verifica que ves:
   - ✅ Todos los archivos en rama "main"
   - ✅ README mostrando correctamente
   - ✅ LICENSE visible
   - ✅ Carpeta src/ con módulos
3. Click en **"Releases"** (en lateral derecho)
   - ✅ Release "v2.0.0" existe
   - ✅ Muestra descripción

---

## ⚠️ Errores Comunes y Soluciones

### Error: "fatal: remote origin already exists"
```powershell
# Solución:
git remote remove origin
# Luego ejecuta 2.3 de nuevo
```

### Error: "fatal: 'origin' does not appear to be a 'git' repository"
```powershell
# Solución: Verifica URL correcta
git remote -v  # Ver URL actual

# Si está mal:
git remote remove origin
# Ejecuta 2.3 nuevamente con URL correcta
```

### Error: "Permission denied"
```powershell
# Solución: Usa Personal Access Token (ver Paso 2.4)
# No uses contraseña de GitHub
```

### Error: "Repository not found"
```powershell
# Verificar:
# 1. ¿URL correcta? (reemplazaste TU_USUARIO?)
# 2. ¿Repositorio es Public?
# 3. ¿Existió el repo en GitHub?

# Ejemplo correcto:
# https://github.com/juanperez/escaneovulnerabilidades.git
# NO:
# https://github.com/TU_USUARIO/escaneovulnerabilidades.git ← Esto fallará
```

---

## ✅ Verificación Final

Ejecuta estos comandos para confirmar:

```powershell
# Ver mi usuario/email configurado
git config --global user.name

# Ver remote configurado
git remote -v

# Ver historial de commits
git log --oneline

# Ver tags
git tag -l
```

Resultado esperado:
```
Tu Nombre
origin  https://github.com/tu-usuario/escaneovulnerabilidades.git (fetch)
origin  https://github.com/tu-usuario/escaneovulnerabilidades.git (push)
abcd123 chore: initial commit v2.0.0
v2.0.0
```

---

## 🔄 Próximas Actualizaciones (futuro)

Cuando hagas cambios en el futuro:

```powershell
# 1. Editar archivos...

# 2. Ver cambios
git status

# 3. Agregar cambios
git add .

# 4. Commit
git commit -m "feat: nueva funcionalidad"

# 5. Push
git push

# 6. Para nueva versión:
git tag v2.0.1
git push origin v2.0.1
```

---

## 📚 Documentación Disponible

Consulta estos archivos en tu carpeta para más info:

- **README.md** - Manual de usuario
- **GITHUB_GUIA_COMPLETA.md** - Guía detallada
- **GIT_GUIA_PASO_A_PASO.md** - Tutorial Git profundo
- **COMPILACION.md** - Compilar a ejecutable
- **CONTRIBUTING.md** - Cómo contribuir
- **CHANGELOG.md** - Historial de cambios
- **RESUMEN_MEJORAS.md** - Resumen de refactorización

---

## 🎯 Resumen Rápido

```powershell
# 1. Crear repo en GitHub (navegador) -> copiar URL

# 2. Ejecutar en PowerShell:
cd "d:\OneDrive\Regional\1 pendientes para analisis\proyectospython\escaneovulnerabilidades"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/escaneovulnerabilidades.git
git push -u origin main

# 3. Crear versión:
git tag v2.0.0
git push origin v2.0.0

# 4. Verificar en GitHub ✅
```

---

## 🚀 ¡LISTO!

Tu proyecto está en GitHub con:
- ✅ Código refactorizado (v2.0.0)
- ✅ Documentación profesional
- ✅ Releases automáticos
- ✅ Versionamiento semántico
- ✅ Licencia Apache 2.0

---

**¿Preguntas?** Lee [GITHUB_GUIA_COMPLETA.md](GITHUB_GUIA_COMPLETA.md)

**Última actualización:** Marzo 3, 2026
