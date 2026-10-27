from tutor_ds.catalog import DEFECTS
from tutor_ds.models import Paradigm, Severity


def test_catalog_has_exactly_six_defects():
    assert sorted(DEFECTS) == ["D1", "D2", "D3", "D4", "D5", "D6"]


def test_every_defect_declares_name_remedy_paradigms_and_severity():
    for code, spec in DEFECTS.items():
        assert spec.code == code
        assert spec.name
        assert spec.remedy.endswith(".")
        assert spec.paradigms
        assert isinstance(spec.severity, Severity)


def test_paradigm_values_are_the_spanish_labels():
    assert [p.value for p in Paradigm] == [
        "funcional",
        "orientado a objetos",
        "modular",
    ]
