# Vulnerability Scanner

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Release](https://github.com/erickson558/escaneovulnerabilidades/actions/workflows/release.yml/badge.svg)](https://github.com/erickson558/escaneovulnerabilidades/actions/workflows/release.yml)

Escaner de vulnerabilidades para equipos Windows, Linux y macOS con interfaz grafica en Tkinter, deteccion basica de riesgos y exportacion de reportes en PDF.

## Que hace el programa

- Detecta paquetes instalados y consulta posibles CVE en NVD.
- Revisa configuraciones inseguras del sistema operativo.
- Identifica cuentas con contrasena debil o ausente (cuando el sistema lo permite).
- Genera reportes PDF con hallazgos y recomendaciones.
- Permite ejecucion por GUI y flujo de configuracion persistente en `config.json`.

## Arquitectura

- `main.py`: punto de entrada recomendado para la app modular.
- `src/backend/`: logica de escaneo y generacion de PDF.
- `src/frontend/`: interfaz Tkinter.
- `src/config.py`: gestion de configuracion.
- `escaneo.py`: script monolitico legacy (se mantiene para compatibilidad y compilacion rapida a `.exe`).

## Requisitos

- Python `3.8+`
- Pip actualizado
- Conexion a internet para consulta de CVE (NVD)
- API key de NVD opcional (mejora limites de uso)

## Instalacion

```bash
git clone https://github.com/erickson558/escaneovulnerabilidades.git
cd escaneovulnerabilidades
python -m venv .venv
```

Windows (PowerShell):

```bash
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

## Ejecucion

Modo modular recomendado:

```bash
python main.py
```

Modo legacy:

```bash
python escaneo.py
```

## Compilar `escaneo.exe` en la misma carpeta que `escaneo.py`

El siguiente comando deja `escaneo.exe` en la raiz del repositorio (misma carpeta de `escaneo.py`) y usa `escaneo.ico` local:

```bash
pyinstaller --noconfirm --clean --onefile --windowed --icon=escaneo.ico --name=escaneo --distpath=. --workpath=build --specpath=. escaneo.py
```

Verificar salida:

```bash
# Windows
Get-Item .\escaneo.exe
```

## Dependencias

Runtime (`requirements.txt`):

- `requests==2.31.0`
- `reportlab==4.0.9`

Build/CI (`requirements-dev.txt`):

- `pyinstaller==6.19.0`

## Versionado

El proyecto usa Semantic Versioning (`MAJOR.MINOR.PATCH`) y tags de release en formato `Vx.x.x`.

Fuente unica de version:

- `src/__init__.py` -> `__version__ = "2.0.4"`

Regla de incremento:

- `PATCH` (`x.x.+1`): correcciones sin romper compatibilidad.
- `MINOR` (`x.+1.0`): nuevas funciones compatibles.
- `MAJOR` (`+1.0.0`): cambios incompatibles.

## Releases automaticos en `main`

Workflow: `.github/workflows/release.yml`

En cada push a `main`, el workflow:

1. Compila `escaneo.exe` en Windows usando `escaneo.py` + `escaneo.ico`.
2. Lee la version desde `src/__init__.py`.
3. Crea tag `V<version>`.
4. Publica un release de GitHub con el `.exe` adjunto.

Si el tag ya existe, el workflow falla para forzar un incremento correcto de version antes del siguiente push.

## Buenas practicas operativas

- No ejecutar el escaneo en produccion sin validacion previa.
- Mantener `config.json` fuera de versionado para datos locales.
- Revisar resultados manualmente antes de aplicar cambios de seguridad.
- Registrar cambios funcionales en `CHANGELOG.md`.

## Licencia

Este proyecto esta bajo Apache License 2.0.

- Texto legal: [LICENSE](LICENSE)
- Aviso del proyecto: [NOTICE](NOTICE)
