from tutor_ds.models import Paradigm
from tutor_ds.report import analyze_source


def _d1(source):
    return [f for f in analyze_source(source).findings if f.code == "D1"]


def test_flags_calculation_and_print_in_same_function():
    source = "def factura(base):\n    total = base * 1.19\n    print('Total:', total)\n    return total\n"
    findings = _d1(source)
    assert len(findings) == 1
    assert findings[0].line == 3
    assert "print" in findings[0].message
    assert "base * 1.19" in findings[0].message


def test_does_not_flag_arithmetic_inside_print_arguments():
    source = "def mostrar(a, b):\n    print(a + b)\n"
    assert _d1(source) == []


def test_does_not_flag_calculation_without_io():
    assert _d1("def area(r):\n    return r * r * 3.14\n") == []


def test_does_not_flag_io_without_calculation():
    assert _d1("def saluda(nombre):\n    print('Hola', nombre)\n") == []


def test_flags_module_level_mixing():
    findings = _d1("total = 100 * 1.19\nprint(total)\n")
    assert len(findings) == 1
    assert findings[0].message.startswith("El módulo mezcla")


def test_nested_function_io_does_not_contaminate_outer_scope():
    source = "def outer(x):\n    y = x * 2\n    def inner():\n        print(y)\n    inner()\n    return y\n"
    assert _d1(source) == []


def test_mixed_source_recommends_modular():
    result = analyze_source("def factura(base):\n    total = base * 1.19\n    print(total)\n    return total\n")
    assert result.recommendation.paradigm is Paradigm.MODULAR
