from tutor_ds.report import analyze_source


def _d3(source):
    return [f for f in analyze_source(source).findings if f.code == "D3"]


def test_identical_function_bodies_are_flagged_once():
    source = (
        "def total_a(base, iva):\n"
        "    subtotal = base + iva\n"
        "    impuesto = subtotal * 0.19\n"
        "    return subtotal + impuesto\n"
        "\n"
        "def total_b(base, iva):\n"
        "    subtotal = base + iva\n"
        "    impuesto = subtotal * 0.19\n"
        "    return subtotal + impuesto\n"
    )
    findings = _d3(source)
    assert len(findings) == 1
    assert "2 lugares" in findings[0].message
    assert "líneas 2, 7" in findings[0].message


def test_short_repeated_blocks_are_ignored():
    source = "def f(x):\n    x += 1\n\ndef g(x):\n    x += 1\n"
    assert _d3(source) == []


def test_single_large_statement_duplicated_is_flagged():
    body = "    return base * 1.19 + base * 0.10 + base * 0.05 - iva\n"
    source = f"def calcular_a(base, iva):\n{body}\ndef calcular_b(base, iva):\n{body}"
    findings = _d3(source)
    assert len(findings) == 1
    assert "2 lugares" in findings[0].message


def test_nested_duplicates_are_reported_once():
    body = (
        "    if cond:\n"
        "        a = 1 + 2\n"
        "        b = a * 3\n"
        "        c = b - 4\n"
        "        d = c / 5\n"
    )
    source = f"def f(cond):\n{body}    return d\n\ndef g(cond):\n{body}    return d\n"
    assert len(_d3(source)) == 1
