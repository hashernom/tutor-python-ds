# Tutor DS

Analizador estático de programas Python que detecta seis defectos de diseño y recomienda un paradigma (funcional, orientado a objetos o modular) con explicaciones y remedios en español.

## Estado

- Fase 1 y fase 2 completas: núcleo de análisis y los seis detectores (D1–D6).
- Fase 3 en progreso: CLI, validación con corpus etiquetado, ejemplos y cobertura.

## Requisitos

Python 3.10 o superior. El analizador no usa dependencias externas.

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Uso

La CLI todavía no está disponible. Para analizar un archivo:

```bash
python3 -c "from pathlib import Path; from tutor_ds.report import analyze_file, render_text; print(render_text(analyze_file(Path('mi_archivo.py'))))"
```

## Pruebas

```bash
pytest
```

## Detectores

| Código | Defecto | Paradigma sugerido |
|---|---|---|
| D1 | Lógica de negocio mezclada con entrada/salida | Modular |
| D2 | Números mágicos | Funcional u OO |
| D3 | Duplicación de código | Funcional |
| D4 | Script largo sin funciones | Funcional o modular |
| D5 | Condicional encadenado por tipo | OO o modular |
| D6 | Datos que viajan juntos | OO |

Cada detector vive en `tutor_ds/detectors/`, se registra en `tutor_ds/detectors/__init__.py` y tiene su archivo de pruebas en `tests/`.

## Estructura

- `tutor_ds/models.py`: tipos del dominio.
- `tutor_ds/catalog.py`: catálogo de defectos, remedios y paradigmas.
- `tutor_ds/ast_utils.py`, `loader.py`, `metrics.py`: lectura y análisis del AST.
- `tutor_ds/detectors/`: los seis detectores.
- `tutor_ds/explanations.py`: mensajes en español.
- `tutor_ds/recommendation.py`: puntaje y recomendación de paradigma.
- `tutor_ds/report.py`: pipeline y reportes de texto y JSON.
- `tests/`: suite de pruebas (`pytest` desde la raíz).
