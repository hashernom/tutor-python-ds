import json

from tutor_ds.explanations import build_findings
from tutor_ds.models import AnalysisResult, Detection, Paradigm
from tutor_ds.report import analyze_file, analyze_source, collect_python_files, render_json, render_text
from tutor_ds.recommendation import recommend


def test_syntax_error_is_reported_without_raising():
    result = analyze_source("def (:\n", path="roto.py")
    assert result.parse_error is not None
    assert "SyntaxError" in result.parse_error
    assert result.findings == ()
    assert result.metrics is None
    assert result.recommendation is None
    assert "Error de sintaxis" in render_text(result)


def test_clean_source_has_no_findings_and_modular_default():
    result = analyze_source("x = 1\n")
    assert result.findings == ()
    assert result.recommendation.paradigm is Paradigm.MODULAR


def test_render_text_lists_finding_and_recommendation():
    finding = build_findings([Detection("D4", 1, context={"statements": 23})])[0]
    result = analyze_source("x = 1\n")
    result = AnalysisResult(
        path="demo.py",
        findings=(finding,),
        metrics=result.metrics,
        recommendation=recommend((finding,), result.metrics),
        parse_error=None,
    )
    text = render_text(result)
    assert "Archivo: demo.py" in text
    assert "Hallazgos (1)" in text
    assert "[D4][ALTA] línea 1:" in text
    assert "Remedio: Divide el script" in text
    assert "Recomendación: funcional" in text
    assert "  - " in text


def test_render_text_reports_no_findings_explicitly():
    assert "Sin hallazgos." in render_text(analyze_source("x = 1\n", path="limpio.py"))


def test_render_json_is_parseable_and_complete():
    result = analyze_source("x = 1\n", path="limpio.py")
    payload = json.loads(render_json([result]))
    assert payload[0]["path"] == "limpio.py"
    assert payload[0]["findings"] == []
    assert payload[0]["recommendation"]["paradigm"] == "modular"
    assert payload[0]["metrics"]["line_count"] == 1


def test_analyze_file_and_collect_python_files(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.py").write_text("y = 2\n", encoding="utf-8")
    (tmp_path / "nota.txt").write_text("hola", encoding="utf-8")

    files = collect_python_files([tmp_path])
    assert [p.name for p in files] == ["a.py", "b.py"]
    assert analyze_file(files[0]).path == str(files[0])
