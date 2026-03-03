# Guía de Git y GitHub - Paso a Paso

## Parte 1: Configuración Inicial de Git

### 1.1 Configurar identidad global (primera vez)
```bash
git config --global user.name "Tu Nombre Completo"
git config --global user.email "tu@email.com"
```

**Explicación:**
- `--global`: Configura Git para todo el sistema
- Esta información se agregará a cada commit

**Verificar configuración:**
```bash
git config --global user.name
git config --global user.email
```

---

## Parte 2: Crear Repositorio Local

### 2.1 Inicializar repositorio en la carpeta del proyecto
```bash
cd escaneovulnerabilidades
git init
```

**Explicación:**
- `git init`: Crea un nuevo repositorio local (`/` carpeta `.git`)
- Esto permite que Git comience a rastrear cambios

**Verificar:**
```bash
git status
```

Debes ver algo como:
```
On branch master

No commits yet

Changes to be committed:
  (nothing)
```

---

## Parte 3: Primera Confirmación (Commit) Local

### 3.1 Ver archivos sin rastrear
```bash
git status
```

**Salida esperada:**
```
Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md
        main.py
        requirements.txt
        ...
```

### 3.2 Agregar todos los archivos al área de preparación
```bash
git add .
```

**Explicación:**
- `git add .`: Prepara todos los cambios (`.` significa "todos")
- Los archivos en `.gitignore` NO se agregan

**Alternativas:**
```bash
git add archivo.py              # Agregar archivo específico
git add src/                    # Agregar carpeta específica
git add *.py                    # Agregar por patrón
```

### 3.3 Verificar cambios preparados
```bash
git status
```

Verás cambios en verde (staged/preparados)

### 3.4 Hacer el primer commit
```bash
git commit -m "feat: v2.0.0 - Refactorización completa"
```

**Explicación:**
- `git commit`: Guarda un punto de control con mensaje
- `-m`: Agrega mensaje de commit (REQUERIDO)
- Mensaje en formato: `tipo: descripción`

**Tipos comunes de commits:**
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de error
- `refactor:` - Cambio de código sin nuevas funciones
- `docs:` - Cambios en documentación
- `style:` - Formato (sin cambios lógicos)

### 3.5 Ver historial de commits
```bash
git log                         # Historial completo
git log --oneline               # Versión resumida
git log --oneline -n 5          # Últimos 5 commits
git log --graph --all --decorate --oneline  # Visualización de ramas
```

---

## Parte 4: Crear Repositorio en GitHub

### 4.1 Ir a GitHub y crear nuevo repositorio

**URL:** https://github.com/new

**Pasos:**
1. Ingresar a GitHub.com (crear cuenta si no tienes)
2. Click en **"+"** → **"New repository"**
3. **Repository name:** `escaneovulnerabilidades` (debe coincidir)
4. **Description:** "Professional vulnerability scanner"
5. **Public:** ✅ Seleccionar (para repositorio público)
6. **Initialize repository:** ❌ NO marcar (ya tenemos commits locales)
7. Click **"Create repository"**

**NO hacer:**
- ❌ No marques "Add a README.md"
- ❌ No marques ".gitignore"
- ❌ No marques "Choose a license"

Ya tenemos estos archivos localmente.

### 4.2 Copiar la URL del repositorio

Después de crear, verás algo como:
```
https://github.com/tu-usuario/escaneovulnerabilidades.git
```

O con SSH:
```
git@github.com:tu-usuario/escaneovulnerabilidades.git
```

Copiar la URL HTTPS (más fácil para principiantes)

---

## Parte 5: Conectar Repositorio Local con GitHub

### 5.1 Agregar remote (enlace a GitHub)
```bash
git remote add origin https://github.com/tu-usuario/escaneovulnerabilidades.git
```

**Explicación:**
- `git remote add`: Agrega un servidor remoto
- `origin`: Nombre del remoto (por convención)
- URL: El enlace de tu repositorio GitHub

### 5.2 Verificar conexión
```bash
git remote -v
```

Debes ver:
```
origin  https://github.com/tu-usuario/escaneovulnerabilidades.git (fetch)
origin  https://github.com/tu-usuario/escaneovulnerabilidades.git (push)
```

### 5.3 Si cometiste error, cambiar el remote
```bash
git remote remove origin
git remote add origin https://github.com/tu-usuario/escaneovulnerabilidades.git
```

---

## Parte 6: Subir Cambios a GitHub (Push)

### 6.1 Primer push a la rama main
```bash
git branch -M main
git push -u origin main
```

**Explicación:**
- `git branch -M main`: Renombra rama `master` a `main`
- `git push`: Sube commits al servidor
- `-u origin main`: Establece upstream (recuerda la rama siguiente)

**¿Credenciales?**
- Si pide usuario/contraseña, use token de GitHub (no contraseña):
- https://github.com/settings/tokens → Generate new token → full repo access

### 6.2 Próximos pushes (más simples)
```bash
git push
```

Ya no necesita `-u` porque la rama está configurada

### 6.3 Ver ramas
```bash
git branch -a
```

Verás:
```
* main
  remotes/origin/main
```

---

## Parte 7: Manejo de Versiones

### 7.1 Crear tags (versiones)
```bash
git tag v2.0.0
git push origin v2.0.0
```

O para todas las etiquetas:
```bash
git push origin --tags
```

### 7.2 Listar tags
```bash
git tag -l
git tag -l --sort=-version:refname
```

### 7.3 Crear release en GitHub

**Método 1: Desde terminal**
```bash
# Necesita GitHub CLI instalado
gh release create v2.0.0 --title "v2.0.0" --notes "Refactorización completa"
```

**Método 2: Desde navegador**
- GitHub.com → Repositorio → "Releases" → "Draft a new release"
- Tag: v2.0.0
- Title: Release v2.0.0
- Description: [agregar cambios]
- Click "Publish release"

---

## Parte 8: Flujo Completo de Trabajo Diario

### 8.1 Hacer cambios
```bash
# Abrir archivo y editar...
# Editar src/backend/scanner.py, etc.
```

### 8.2 Ver cambios
```bash
git status              # Ver qué cambió
git diff archivo.py     # Ver diferencias específicas
```

### 8.3 Commit de cambios
```bash
git add .               # Preparar cambios
git commit -m "fix: mejorar rendimiento del scanner"
```

### 8.4 Subir a GitHub
```bash
git push
```

### 8.5 Crear nueva versión
```bash
# Editar src/__init__.py y cambiar __version__ = "2.0.1"
git add src/__init__.py
git commit -m "bump: versión a 2.0.1"
git tag v2.0.1
git push
git push origin v2.0.1
```

---

## Parte 9: Seguridad y Buenas Prácticas

### 9.1 Nunca commitear
- ❌ Contraseñas o API keys
- ❌ Archivos locales de configuración
- ❌ Carpetas node_modules, __pycache__
- ❌ Archivos compilados

Usar `.gitignore` para esto (ya incluido)

### 9.2 Mensajes de commit claros
❌ Malo:
```bash
git commit -m "cambios"
git commit -m "fix bug"
```

✅ Bueno:
```bash
git commit -m "fix: corregir timeout en escaneo NVD"
git commit -m "feat: agregar validación de API key"
git commit -m "docs: actualizar instrucciones de instalación"
```

### 9.3 Commits pequeños y frecuentes
✅ Preferible: Varios commits pequeños
```bash
git commit -m "refactor: separar config en módulo"
git commit -m "feat: agregar logging estructurado"
git commit -m "docs: actualizar README"
```

❌ No recomendado: Un commit gigante con todo

---

## Parte 10: Formato Convencional de Commits

Usar el formato estándar `Conventional Commits`:

```
tipo(alcance): descripción

[cuerpo opcional]

[pie opcional]
```

**Ejemplos:**

```bash
# Nueva funcionalidad
git commit -m "feat(scanner): agregar soporte para escaneo de puertos"

# Corrección
git commit -m "fix(pdf): corregir encoding en reportes en español"

# Con cuerpo (cambios complejos)
git commit -m "refactor(backend): separar lógica de escaneo

- Crear clase VulnerabilityScanner
- Implementar patrón de inyección de dependencias
- Mejorar manejo de excepciones"

# Con múltiples aspectos
git commit -m "chore(deps): actualizar reportlab a 4.0.9

Cambia:
- reportlab: 4.0.7 → 4.0.9
- requests: 2.30.0 → 2.31.0"
```

**Tipos válidos:**
- **feat**: Nueva funcionalidad
- **fix**: Corrección de bug
- **refactor**: Cambio de estructura
- **docs**: Documentación
- **style**: Formato (espacios, comillas, etc.)
- **test**: Agregar/modificar tests
- **chore**: Mantenimiento, dependencias
- **ci**: Configuración CI/CD

---

## Parte 11: Versionamiento Semántico (SemVer)

Formato: `MAJOR.MINOR.PATCH`

- **MAJOR** (X.0.0): Cambios incompatibles
- **MINOR** (0.X.0): Nuevas funciones (compatibles)
- **PATCH** (0.0.X): Correcciones de bugs

**Ejemplos:**

```
v1.0.0 → v1.0.1   (fix: parche)
v1.0.1 → v1.1.0   (feat: nueva función)
v1.1.0 → v2.0.0   (refactor: cambio incompatible)
```

**Incrementar versión:**

1. Editar `src/__init__.py`:
```python
__version__ = "2.0.1"
```

2. Commit:
```bash
git commit -m "bump: v2.0.1 - Correcciones menores"
```

3. Tag:
```bash
git tag v2.0.1
git push origin main v2.0.1
```

---

## Resumen de Comandos Esenciales

```bash
# Configuración
git config --global user.name "Nombre"
git config --global user.email "email@com"

# Local
git init                        # Crear repositorio
git status                      # Ver cambios
git add .                       # Preparar cambios
git commit -m "mensaje"         # Guardar versión
git log --oneline               # Ver historial

# Remoto (GitHub)
git remote add origin URL       # Conectar
git push                        # Subir cambios
git pull                        # Descargar cambios
git fetch                       # Obtener cambios remoto

# Versiones
git tag v1.0.0                  # Crear versión
git push origin --tags          # Subir versiones
git tag -l                      # Listar versiones
```

---

**¡Ahora estás listo para trabajar con Git como profesional! 🚀**

Para preguntas, consulta: https://git-scm.com/book/en/v2
