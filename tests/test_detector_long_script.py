from tutor_ds.models import Severity
from tutor_ds.report import analyze_source


def _script(n):
    return "".join(f"x{i} = {i}\n" for i in range(n))


def _d4(source):
    return [f for f in analyze_source(source).findings if f.code == "D4"]


def test_fifteen_top_level_statements_trigger_medium_severity():
    findings = _d4(_script(15))
    assert len(findings) == 1
    assert findings[0].severity is Severity.MEDIA
    assert findings[0].message == "Script largo sin funciones: 15 sentencias a nivel superior y ninguna definición de función o clase."


def test_thirty_statements_trigger_high_severity():
    assert _d4(_script(30))[0].severity is Severity.ALTA


def test_short_script_is_not_flagged():
    assert _d4(_script(10)) == []


def test_script_with_one_function_is_not_flagged():
    source = _script(20) + "\ndef main():\n    pass\n"
    assert _d4(source) == []


def test_long_class_only_file_is_not_flagged():
    source = _script(20) + "\nclass Pedido:\n    pass\n"
    assert _d4(source) == []


def test_control_flow_statements_count_toward_the_total():
    source = "if True:\n" + "".join(f"    x{i} = {i}\n" for i in range(16))
    assert len(_d4(source)) == 1
