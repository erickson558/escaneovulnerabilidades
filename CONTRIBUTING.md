# Contributing

Gracias por contribuir a `escaneovulnerabilidades`.

## Flujo recomendado

1. Crear rama desde `main`:

```bash
git checkout -b feat/mi-cambio
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. Ejecutar la app y validar manualmente:

```bash
python main.py
```

4. Si aplica, recompilar ejecutable:

```bash
pyinstaller --noconfirm --clean --onefile --windowed --icon=escaneo.ico --name=escaneo --distpath=. --workpath=build --specpath=. escaneo.py
```

5. Actualizar version y changelog.

6. Commit usando Conventional Commits:

```bash
git commit -m "feat(scanner): descripcion breve"
```

7. Push y Pull Request.

## Politica de versionado

Este repositorio usa SemVer con tags `Vx.x.x`.

Fuente unica de version:

- `src/__init__.py`

Incremento:

- `PATCH`: fixes y ajustes sin romper compatibilidad.
- `MINOR`: funcionalidades nuevas compatibles.
- `MAJOR`: cambios incompatibles.

Antes de merge a `main`:

- Incrementar `__version__` segun el tipo de cambio.
- Agregar entrada en `CHANGELOG.md`.

## Checklist de PR

- [ ] Codigo funcional en Windows, Linux o macOS segun alcance.
- [ ] README/CHANGELOG actualizados si hubo cambios funcionales.
- [ ] Version incrementada en `src/__init__.py`.
- [ ] Sin secretos en commits.
- [ ] Build local validado cuando se toca distribucion `.exe`.

## Estilo de codigo

- Seguir PEP 8.
- Mantener funciones pequenas y con responsabilidad unica.
- Manejar errores esperables con mensajes claros.
- Agregar comentarios solo cuando la logica no sea obvia.

## Seguridad

- No subir API keys ni archivos locales sensibles.
- Revisar cuidadosamente cambios en escaneo y salida de reportes.

## Licencia

Al contribuir, aceptas que tu aporte se publica bajo Apache License 2.0.
