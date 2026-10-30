from tutor_ds.models import Severity
from tutor_ds.report import analyze_source


def _d2(source):
    return [f for f in analyze_source(source).findings if f.code == "D2"]


def test_repeated_literal_in_arithmetic_is_flagged():
    findings = _d2("def total(base, propina):\n    return base * 1.19 + base * 0.10\n")
    assert [f.evidence for f in findings] == ["1.19", "0.10"]
    assert findings[0].severity is Severity.MEDIA


def test_single_literal_in_comparison_is_flagged():
    findings = _d2("def categoria(edad):\n    if edad > 65:\n        return 'mayor'\n    return 'adulto'\n")
    assert [f.evidence for f in findings] == ["65"]
    assert findings[0].message == "Número mágico `65`: aparece 1 vez en comparaciones (línea 2)."


def test_trivial_literals_and_named_constants_are_ignored():
    source = "IVA = 0.19\n\ndef total(base, activo):\n    if activo == True:\n        return base + 1 + 0 + 2\n    return base * IVA\n"
    assert _d2(source) == []


def test_three_occurrences_raise_severity():
    findings = _d2("def f(a):\n    return a * 7 + 7 * a + (7 - a)\n")
    assert findings[0].severity is Severity.ALTA
    assert findings[0].message == "Número mágico `7`: aparece 3 veces en operaciones (línea 2)."


def test_repeated_literal_outside_rules_is_still_flagged():
    findings = _d2("def f(a, b):\n    x = 4\n    y = 4\n    return a + b\n")
    assert [f.evidence for f in findings] == ["4"]
    assert findings[0].message == "Número mágico `4`: aparece 2 veces en el archivo (líneas 2, 3)."
