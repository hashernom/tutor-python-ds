from tutor_ds.explanations import build_findings
from tutor_ds.models import Detection, Paradigm, SourceMetrics
from tutor_ds.recommendation import recommend


def _metrics(**overrides):
    base = dict(
        line_count=30, function_count=0, class_count=0, method_count=0,
        top_level_statements=20, max_nesting_depth=1, io_call_count=0,
    )
    base.update(overrides)
    return SourceMetrics(**base)


def _finding(code, line, context):
    return build_findings([Detection(code, line, context=context)])[0]


def test_three_type_switches_recommend_oop():
    findings = [
        _finding("D5", line, {"variable": "tipo", "branches": 3, "values": ["'a'", "'b'", "'c'"]})
        for line in (3, 9, 15)
    ]
    rec = recommend(findings, _metrics())
    assert rec.paradigm is Paradigm.OO
    assert rec.scores[Paradigm.OO] > rec.scores[Paradigm.MODULAR]
    assert 0.5 < rec.confidence < 1.0
    assert any("apunta a un diseño orientado a objetos" in r for r in rec.reasons)


def test_mixed_io_script_recommends_modular():
    findings = [
        _finding("D1", 4, {"scope_kind": "módulo", "scope": "módulo", "calculation": "total * 1.19", "io": "print"}),
        _finding("D4", 1, {"statements": 23}),
    ]
    rec = recommend(findings, _metrics())
    assert rec.paradigm is Paradigm.MODULAR


def test_clean_object_oriented_file_stays_oop():
    metrics = _metrics(function_count=0, class_count=2, method_count=4, top_level_statements=2)
    rec = recommend((), metrics)
    assert rec.paradigm is Paradigm.OO
    assert rec.confidence == 1.0
    assert any("clases" in r for r in rec.reasons)


def test_clean_functional_file_recommends_functional():
    rec = recommend((), _metrics(function_count=3, top_level_statements=3))
    assert rec.paradigm is Paradigm.FUNCIONAL


def test_without_any_evidence_recommends_modular_with_disclaimer():
    rec = recommend((), _metrics(function_count=1, top_level_statements=1))
    assert rec.paradigm is Paradigm.MODULAR
    assert rec.confidence == 1.0
    assert rec.reasons[0].startswith("No se detectaron defectos")
