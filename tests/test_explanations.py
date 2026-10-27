from tutor_ds.explanations import build_findings
from tutor_ds.models import Detection, Severity


def _build(code, context, **kwargs):
    kwargs.setdefault("line", 1)
    return build_findings([Detection(code, **kwargs, context=context)])[0]


def test_d1_function_message():
    f = _build("D1", {"scope_kind": "función", "scope": "factura", "calculation": "base * 1.19", "io": "print"}, line=4)
    assert f.message == "La función `factura` mezcla cálculo de negocio (`base * 1.19`) con E/S (`print`)."
    assert f.line == 4
    assert f.severity is Severity.ALTA
    assert f.defect == "Lógica de negocio mezclada con entrada/salida"


def test_d1_module_message():
    f = _build("D1", {"scope_kind": "módulo", "scope": "módulo", "calculation": "total * 1.19", "io": "print"})
    assert f.message == "El módulo mezcla cálculo de negocio (`total * 1.19`) con E/S (`print`)."


def test_d2_message_pluralizes_occurrences_and_lines():
    f = _build("D2", {"value": "0.19", "count": 2, "lines": [12, 18], "usage": "operaciones"})
    assert f.message == "Número mágico `0.19`: aparece 2 veces en operaciones (líneas 12, 18)."


def test_d2_message_uses_singular_for_one_occurrence():
    f = _build("D2", {"value": "65", "count": 1, "lines": [7], "usage": "comparaciones"})
    assert f.message == "Número mágico `65`: aparece 1 vez en comparaciones (línea 7)."


def test_d3_message():
    f = _build("D3", {"count": 2, "lines": [3, 11], "nodes": 9, "snippet": "print(total)"})
    assert f.message == "Se repite un bloque equivalente de 9 nodos en 2 lugares (líneas 3, 11): `print(total)`."


def test_d4_message():
    f = _build("D4", {"statements": 23})
    assert f.message == "Script largo sin funciones: 23 sentencias a nivel superior y ninguna definición de función o clase."


def test_d5_message_lists_values():
    f = _build("D5", {"variable": "tipo", "branches": 4, "values": ["'admin'", "'docente'", "'estudiante'"]})
    assert f.message == "Condicional encadenado: 4 ramas comparan `tipo` con los valores `'admin'`, `'docente'`, `'estudiante'`."


def test_d5_message_truncates_after_four_values():
    f = _build("D5", {"variable": "tipo", "branches": 6, "values": ["'a'", "'b'", "'c'", "'d'", "'e'"]})
    assert f.message == (
        "Condicional encadenado: 6 ramas comparan `tipo` con los valores "
        "`'a'`, `'b'`, `'c'`, `'d'`, …."
    )


def test_d6_message_joins_function_and_parameter_names():
    f = _build("D6", {"params": ["base", "iva", "descuento"], "functions": ["calc_total", "calc_iva"]})
    assert f.message == (
        "Datos que viajan juntos: las funciones `calc_total` y `calc_iva` "
        "repiten los parámetros `base`, `iva`, `descuento`."
    )


def test_findings_are_sorted_by_line_then_code():
    detections = [
        Detection("D4", 10, context={"statements": 20}),
        Detection("D1", 2, context={"scope_kind": "función", "scope": "f", "calculation": "a * 2", "io": "print"}),
        Detection("D2", 2, context={"value": "3", "count": 2, "lines": [2, 5], "usage": "operaciones"}),
    ]
    assert [(f.line, f.code) for f in build_findings(detections)] == [(2, "D1"), (2, "D2"), (10, "D4")]


def test_detector_severity_overrides_catalog_default():
    f = _build("D4", {"statements": 20}, severity=Severity.MEDIA)
    assert f.severity is Severity.MEDIA
