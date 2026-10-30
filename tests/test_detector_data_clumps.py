from tutor_ds.report import analyze_source


def _d6(source):
    return [f for f in analyze_source(source).findings if f.code == "D6"]


def test_two_functions_sharing_three_params_are_flagged():
    source = (
        "def calc_total(base, iva, descuento):\n"
        "    return base + iva - descuento\n"
        "\n"
        "def calc_recibo(base, iva, descuento):\n"
        "    return base + iva - descuento\n"
    )
    findings = _d6(source)
    assert len(findings) == 1
    assert findings[0].message == (
        "Datos que viajan juntos: las funciones `calc_recibo` y `calc_total` "
        "repiten los parámetros `base`, `descuento`, `iva`."
    )


def test_two_shared_params_are_not_flagged():
    source = (
        "def a(base, iva):\n    return base + iva\n\ndef b(base, iva):\n    return base * iva\n"
    )
    assert _d6(source) == []


def test_self_does_not_count_as_shared_data():
    source = (
        "class Factura:\n"
        "    def total(self, base, iva):\n"
        "        return base + iva\n"
        "    def subtotal(self, base, iva):\n"
        "        return base - iva\n"
    )
    assert _d6(source) == []


def test_three_functions_sharing_the_same_triple_are_reported_once():
    source = (
        "def a(base, iva, descuento):\n    return 1\n"
        "\n"
        "def b(base, iva, descuento):\n    return 2\n"
        "\n"
        "def c(base, iva, descuento):\n    return 3\n"
    )
    findings = _d6(source)
    assert len(findings) == 1
    assert "`a`, `b` y `c`" in findings[0].message
