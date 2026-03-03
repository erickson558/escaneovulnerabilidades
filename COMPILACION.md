# Compilacion

Guia rapida para generar el ejecutable de Windows.

## Objetivo

Generar `escaneo.exe` en la misma carpeta donde esta `escaneo.py`, usando el icono `escaneo.ico` de esa misma carpeta.

## Requisitos

- Python 3.8+
- Dependencias instaladas
- PyInstaller

Instalacion sugerida:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Comando de compilacion

Desde la raiz del repositorio:

```bash
pyinstaller --noconfirm --clean --onefile --windowed --icon=escaneo.ico --name=escaneo --distpath=. --workpath=build --specpath=. escaneo.py
```

## Resultado esperado

- `escaneo.exe` en la raiz del proyecto.
- `build/` como carpeta temporal de compilacion.
- `escaneo.spec` actualizado por PyInstaller.

## Verificacion basica

```bash
# Windows PowerShell
Get-Item .\escaneo.exe
```

Abrir `escaneo.exe` y validar:

- Inicio correcto de GUI.
- Escaneo basico.
- Exportacion PDF.

## Limpieza opcional

Si deseas limpiar artefactos temporales y recompilar:

```bash
Remove-Item -Recurse -Force .\build -ErrorAction SilentlyContinue
```

## CI/CD

El workflow `.github/workflows/release.yml` repite esta compilacion en `windows-latest` para publicar el `.exe` en cada release de `main`.
