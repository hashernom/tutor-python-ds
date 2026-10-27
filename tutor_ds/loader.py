import ast
from pathlib import Path

from tutor_ds.models import AnalysisContext, DetectorConfig


def build_context(
    source: str,
    *,
    path: str | None = None,
    config: DetectorConfig | None = None,
) -> AnalysisContext:
    tree = ast.parse(source)
    return AnalysisContext(
        source=source,
        tree=tree,
        lines=tuple(source.splitlines()),
        config=DetectorConfig() if config is None else config,
        path=path,
    )


def read_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def format_parse_error(exc: SyntaxError) -> str:
    return f"SyntaxError: {exc.msg} (línea {exc.lineno})"
