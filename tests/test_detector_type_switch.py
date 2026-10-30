from tutor_ds.models import Severity
from tutor_ds.report import analyze_source


def _d5(source):
    return [f for f in analyze_source(source).findings if f.code == "D5"]


def test_three_branch_chain_on_same_variable_is_flagged():
    source = (
        "def enviar(tipo):\n"
        "    if tipo == 'admin':\n"
        "        return 1\n"
        "    elif tipo == 'docente':\n"
        "        return 2\n"
        "    elif tipo == 'estudiante':\n"
        "        return 3\n"
        "    return 0\n"
    )
    findings = _d5(source)
    assert len(findings) == 1
    assert findings[0].severity is Severity.MEDIA
    assert findings[0].message == (
        "Condicional encadenado: 3 ramas comparan `tipo` con los valores "
        "`'admin'`, `'docente'`, `'estudiante'`."
    )


def test_five_branches_raise_severity_to_high():
    source = "def f(tipo):\n" + "".join(
        f"    {'if' if i == 0 else 'elif'} tipo == {i}:\n        return {i}\n" for i in range(5)
    )
    assert _d5(source)[0].severity is Severity.ALTA


def test_two_branch_chain_is_not_flagged():
    source = "def f(tipo):\n    if tipo == 1:\n        return 1\n    elif tipo == 2:\n        return 2\n    return 0\n"
    assert _d5(source) == []


def test_chain_on_different_variables_is_not_flagged():
    source = (
        "def f(a, b, c):\n"
        "    if a == 1:\n"
        "        return 1\n"
        "    elif b == 2:\n"
        "        return 2\n"
        "    elif c == 3:\n"
        "        return 3\n"
        "    return 0\n"
    )
    assert _d5(source) == []


def test_isinstance_chain_is_flagged():
    source = (
        "def f(x):\n"
        "    if isinstance(x, int):\n"
        "        return 1\n"
        "    elif isinstance(x, str):\n"
        "        return 2\n"
        "    elif isinstance(x, float):\n"
        "        return 3\n"
        "    return 0\n"
    )
    findings = _d5(source)
    assert len(findings) == 1
    assert findings[0].evidence == "x"
