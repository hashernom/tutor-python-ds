import ast
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class Paradigm(str, Enum):
    FUNCIONAL = "funcional"
    OO = "orientado a objetos"
    MODULAR = "modular"


class Severity(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


SEVERITY_WEIGHT: dict[Severity, float] = {
    Severity.ALTA: 3.0,
    Severity.MEDIA: 2.0,
    Severity.BAJA: 1.0,
}
SECONDARY_WEIGHT: float = 0.4
SEVERITY_ORDER: dict[Severity, int] = {
    Severity.BAJA: 0,
    Severity.MEDIA: 1,
    Severity.ALTA: 2,
}


@dataclass(frozen=True)
class DefectSpec:
    code: str
    name: str
    remedy: str
    paradigms: tuple[Paradigm, ...]
    severity: Severity


@dataclass(frozen=True)
class Detection:
    code: str
    line: int
    column: int = 0
    context: Mapping[str, Any] = field(default_factory=dict)
    severity: Severity | None = None


@dataclass(frozen=True)
class Finding:
    code: str
    defect: str
    message: str
    remedy: str
    line: int
    column: int
    severity: Severity
    paradigms: tuple[Paradigm, ...]
    evidence: str


@dataclass(frozen=True)
class SourceMetrics:
    line_count: int
    function_count: int
    class_count: int
    method_count: int
    top_level_statements: int
    max_nesting_depth: int
    io_call_count: int


@dataclass(frozen=True)
class Recommendation:
    paradigm: Paradigm
    scores: Mapping[Paradigm, float]
    confidence: float
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisResult:
    path: str | None
    findings: tuple[Finding, ...]
    metrics: SourceMetrics | None
    recommendation: Recommendation | None
    parse_error: str | None


@dataclass(frozen=True)
class DetectorConfig:
    magic_min_occurrences: int = 2
    duplicate_min_nodes: int = 8
    long_script_min_statements: int = 15
    long_script_high_statements: int = 30
    type_switch_min_branches: int = 3
    type_switch_high_branches: int = 5
    data_clump_min_params: int = 3
    max_findings_per_detector: int = 10


@dataclass(frozen=True)
class AnalysisContext:
    source: str
    tree: ast.Module
    lines: tuple[str, ...]
    config: DetectorConfig = field(default_factory=DetectorConfig)
    path: str | None = None

    def segment(self, node: ast.AST, limit: int = 60) -> str:
        text = ast.get_source_segment(self.source, node)
        if not text:
            return ""
        collapsed = " ".join(text.split())
        if len(collapsed) > limit:
            return collapsed[: limit - 1] + "…"
        return collapsed
