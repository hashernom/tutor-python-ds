from collections.abc import Sequence

from tutor_ds.models import (
    SECONDARY_WEIGHT,
    SEVERITY_WEIGHT,
    Finding,
    Paradigm,
    Recommendation,
    SourceMetrics,
)

_PRIORITY: tuple[Paradigm, ...] = (Paradigm.FUNCIONAL, Paradigm.OO, Paradigm.MODULAR)
_DISCLAIMER = (
    "No se detectaron defectos de diseño; no hay evidencia para cambiar "
    "la estructura actual."
)
_MAX_REASONS = 4
_MAX_FINDING_REASONS = 3


def _score_findings(findings: Sequence[Finding]) -> dict[Paradigm, float]:
    scores = {paradigm: 0.0 for paradigm in _PRIORITY}
    for finding in findings:
        weight = SEVERITY_WEIGHT[finding.severity]
        scores[finding.paradigms[0]] += weight
        for paradigm in finding.paradigms[1:]:
            scores[paradigm] += SECONDARY_WEIGHT * weight
    return scores


def _is_short_script(metrics: SourceMetrics) -> bool:
    return (
        metrics.top_level_statements <= 15
        and metrics.function_count == 0
        and metrics.class_count == 0
    )


def _apply_structural_scores(
    scores: dict[Paradigm, float], metrics: SourceMetrics
) -> None:
    if metrics.class_count >= 1:
        scores[Paradigm.OO] += 2.0
    if metrics.method_count >= 3:
        scores[Paradigm.OO] += 1.0
    if metrics.function_count >= 2:
        scores[Paradigm.FUNCIONAL] += 1.5
    if _is_short_script(metrics):
        scores[Paradigm.MODULAR] += 1.0


def _finding_reasons(findings: Sequence[Finding]) -> list[str]:
    ordered = sorted(
        findings,
        key=lambda finding: (-SEVERITY_WEIGHT[finding.severity], finding.line),
    )
    return [
        f"{finding.defect} (línea {finding.line}) apunta a un diseño "
        f"{finding.paradigms[0].value}."
        for finding in ordered[:_MAX_FINDING_REASONS]
    ]


def _structural_reasons(metrics: SourceMetrics) -> list[str]:
    reasons: list[str] = []
    if metrics.class_count >= 1:
        noun = "clase" if metrics.class_count == 1 else "clases"
        reasons.append(f"El archivo ya define {metrics.class_count} {noun}.")
    if metrics.function_count >= 2:
        reasons.append(
            f"El archivo ya organiza la lógica en {metrics.function_count} funciones."
        )
    if _is_short_script(metrics):
        reasons.append("El archivo es un script corto sin funciones ni clases.")
    return reasons


def _build_reasons(
    findings: Sequence[Finding], metrics: SourceMetrics
) -> tuple[str, ...]:
    reasons = _finding_reasons(findings)
    if not findings:
        reasons = [_DISCLAIMER]
    for reason in _structural_reasons(metrics):
        if len(reasons) >= _MAX_REASONS:
            break
        reasons.append(reason)
    return tuple(reasons)


def recommend(findings: Sequence[Finding], metrics: SourceMetrics) -> Recommendation:
    scores = _score_findings(findings)
    _apply_structural_scores(scores, metrics)
    if all(score == 0 for score in scores.values()):
        scores[Paradigm.MODULAR] = 1.0
    best_score = max(scores.values())
    paradigm = next(
        candidate for candidate in _PRIORITY if scores[candidate] == best_score
    )
    total = sum(scores.values())
    confidence = round(best_score / total, 3) if total else 0.0
    return Recommendation(
        paradigm=paradigm,
        scores={candidate: round(score, 3) for candidate, score in scores.items()},
        confidence=confidence,
        reasons=_build_reasons(findings, metrics),
    )
