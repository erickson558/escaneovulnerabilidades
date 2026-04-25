# Vulnerability Scanner

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Release](https://github.com/erickson558/escaneovulnerabilidades/actions/workflows/release.yml/badge.svg)](https://github.com/erickson558/escaneovulnerabilidades/actions/workflows/release.yml)

Escaner de vulnerabilidades para equipos Windows, Linux y macOS con interfaz grafica en Tkinter, deteccion basica de riesgos, exportacion de reportes en PDF, soporte multi-idioma (ES/EN) y boton de donacion.

## Que hace el programa

- Detecta paquetes instalados y consulta posibles CVE en NVD.
- Revisa configuraciones inseguras del sistema operativo.
- Identifica cuentas con contrasena debil o ausente (cuando el sistema lo permite).
- Genera reportes PDF con hallazgos y recomendaciones.
- Interfaz en español e inglés, cambiable en tiempo de ejecución.
- Permite ejecucion por GUI y flujo de configuracion persistente en `config.json`.

## Apoya el proyecto

Si te resulta útil, puedes invitarme una cerveza:

[![Buy me a Beer](https://img.shields.io/badge/PayPal-Cómprame%20una%20Cerveza-orange?logo=paypal)](https://www.paypal.com/donate/?hosted_button_id=ZABFRXC2P3JQN)

## Arquitectura

- `main.py`: punto de entrada recomendado para la app modular.
- `src/backend/`: logica de escaneo y generacion de PDF.
- `src/frontend/`: interfaz Tkinter con i18n y boton de donacion.
- `src/i18n.py`: diccionario de traducciones ES/EN.
- `src/config.py`: gestion de configuracion (incluye clave `language`).
- `escaneo.py`: script monolitico legacy (se mantiene para compilacion rapida a `.exe`).

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

- `requests==2.32.5`
- `reportlab==4.4.10`

Build/CI (`requirements-dev.txt`):

- `pyinstaller==6.19.0`

## Multi-idioma

La aplicacion soporta español (`es`) e inglés (`en`).
El idioma se puede cambiar en tiempo de ejecucion desde el selector en la parte inferior de la ventana.
El idioma seleccionado se persiste en `config.json` con la clave `language`.

## Boton de Donacion

La interfaz incluye un boton **"Cómprame una Cerveza / Buy me a Beer"** que abre la pagina de donacion de PayPal en el navegador.

## Versionado

El proyecto usa Semantic Versioning (`MAJOR.MINOR.PATCH`) y tags de release en formato `Vx.x.x`.

Fuente unica de version:

- `src/__init__.py` -> `__version__ = "2.1.0"`

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
