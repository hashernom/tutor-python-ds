import json
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from tutor_ds.detectors import run_detectors
from tutor_ds.explanations import build_findings
from tutor_ds.loader import build_context, format_parse_error, read_source
from tutor_ds.metrics import compute_metrics
from tutor_ds.models import (
    AnalysisResult,
    DetectorConfig,
    Finding,
    Recommendation,
    SourceMetrics,
)
from tutor_ds.recommendation import recommend

_SOURCE_PLACEHOLDER = "<fuente>"


def _display_path(result: AnalysisResult) -> str:
    return result.path if result.path is not None else _SOURCE_PLACEHOLDER


def _metrics_to_dict(metrics: SourceMetrics | None) -> dict[str, Any] | None:
    return None if metrics is None else asdict(metrics)


def _finding_to_dict(finding: Finding) -> dict[str, Any]:
    return {
        "code": finding.code,
        "defect": finding.defect,
        "message": finding.message,
        "remedy": finding.remedy,
        "line": finding.line,
        "column": finding.column,
        "severity": finding.severity.value,
        "paradigms": [paradigm.value for paradigm in finding.paradigms],
        "evidence": finding.evidence,
    }


def _recommendation_to_dict(
    recommendation: Recommendation | None,
) -> dict[str, Any] | None:
    if recommendation is None:
        return None
    return {
        "paradigm": recommendation.paradigm.value,
        "scores": {
            paradigm.value: score for paradigm, score in recommendation.scores.items()
        },
        "confidence": recommendation.confidence,
        "reasons": list(recommendation.reasons),
    }


def to_dict(result: AnalysisResult) -> dict[str, Any]:
    return {
        "path": result.path,
        "parse_error": result.parse_error,
        "metrics": _metrics_to_dict(result.metrics),
        "findings": [_finding_to_dict(finding) for finding in result.findings],
        "recommendation": _recommendation_to_dict(result.recommendation),
    }


def render_text(result: AnalysisResult) -> str:
    lines = [f"Archivo: {_display_path(result)}"]
    if result.parse_error is not None:
        lines.append(f"Error de sintaxis: {result.parse_error}")
        return "\n".join(lines)
    metrics = result.metrics
    recommendation = result.recommendation
    lines.append(
        f"Líneas: {metrics.line_count} | Funciones: {metrics.function_count} | "
        f"Clases: {metrics.class_count} | "
        f"Sentencias superiores: {metrics.top_level_statements}"
    )
    lines.append("")
    lines.append(f"Hallazgos ({len(result.findings)})")
    if result.findings:
        for finding in result.findings:
            lines.append(
                f"  [{finding.code}][{finding.severity.value.upper()}] "
                f"línea {finding.line}: {finding.message}"
            )
            lines.append(f"      Remedio: {finding.remedy}")
    else:
        lines.append("  Sin hallazgos.")
    lines.append("")
    lines.append(
        f"Recomendación: {recommendation.paradigm.value} "
        f"(confianza {recommendation.confidence:.0%})"
    )
    lines.extend(f"  - {reason}" for reason in recommendation.reasons)
    return "\n".join(lines)


def render_json(results: Iterable[AnalysisResult]) -> str:
    return json.dumps(
        [to_dict(result) for result in results], ensure_ascii=False, indent=2
    )


def analyze_source(
    source: str,
    *,
    path: str | None = None,
    config: DetectorConfig | None = None,
) -> AnalysisResult:
    try:
        ctx = build_context(source, path=path, config=config)
    except SyntaxError as exc:
        return AnalysisResult(
            path=path,
            findings=(),
            metrics=None,
            recommendation=None,
            parse_error=format_parse_error(exc),
        )
    metrics = compute_metrics(ctx.tree, ctx.lines)
    findings = build_findings(run_detectors(ctx))
    return AnalysisResult(
        path=path,
        findings=findings,
        metrics=metrics,
        recommendation=recommend(findings, metrics),
        parse_error=None,
    )


def analyze_file(
    path: Path, *, config: DetectorConfig | None = None
) -> AnalysisResult:
    return analyze_source(read_source(path), path=str(path), config=config)


def analyze_paths(
    paths: Iterable[Path], *, config: DetectorConfig | None = None
) -> list[AnalysisResult]:
    return [analyze_file(path, config=config) for path in paths]


def collect_python_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        else:
            files.append(path)
    return files
