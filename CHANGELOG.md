# Changelog

Todos los cambios relevantes se documentan aqui.

El formato sigue Keep a Changelog y Semantic Versioning.

## [2.0.4] - 2026-03-03

### Changed
- Incremento de version patch a `2.0.4` para el siguiente release en `main`.
- Sincronizacion de version en script legacy y README.

### Build
- Recompilacion de `escaneo.exe` en la raiz del proyecto usando `escaneo.ico`.

## [2.0.3] - 2026-03-03

### Changed
- Incremento de version patch a `2.0.3` siguiendo SemVer.
- Referencias de version sincronizadas en la documentacion y script legacy.

### Build
- Recompilacion local de `escaneo.exe` en la raiz del repositorio, usando `escaneo.ico` local.

### Documentation
- Ajustes finales de README/CHANGELOG para dejar el flujo de release en `main` documentado con tags `Vx.x.x`.

## [2.0.2] - 2026-03-03

### Changed
- Version unificada en una sola fuente de verdad (`src/__init__.py`).
- `main.py`, GUI y generador PDF ahora consumen la version centralizada.
- `escaneo.py` actualizado para reflejar la version actual del proyecto.

### Build
- Estandar de compilacion actualizado para generar `escaneo.exe` en la raiz del repositorio (misma carpeta de `escaneo.py`).
- Compilacion configurada para usar `escaneo.ico` local en la raiz.

### CI/CD
- Workflow de release reemplazado para ejecutarse en cada push a `main`.
- El workflow compila `escaneo.exe`, crea tag `Vx.x.x` y publica release con el ejecutable adjunto.
- Se agrega validacion para evitar reutilizar tags y forzar incremento de version.

### Documentation
- README reescrito con instalacion, ejecucion, dependencias, compilacion y proceso de release.
- CONTRIBUTING actualizado con politica de versionado y flujo de contribucion.
- COMPILACION actualizado con comandos reales y reproducibles.
- Se agrega archivo `NOTICE` para acompanar Apache License 2.0.

## [2.0.1] - 2026-03-03

### Changed
- Optimizaciones de build del ejecutable.

## [2.0.0] - 2026-03-03

### Added
- Refactorizacion modular en `src/` (backend, frontend, config, logger, utils).
- Interfaz grafica estructurada y separacion de responsabilidades.
- GitHub Actions inicial para automatizacion de release.

## [1.3.6] - 2025-05-13

### Added
- Version monolitica inicial en `escaneo.py`.
- Escaneo basico y exportacion PDF.
