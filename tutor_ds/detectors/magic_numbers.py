import ast
from dataclasses import dataclass

from tutor_ds.ast_utils import is_arithmetic, parent_map
from tutor_ds.models import AnalysisContext, Detection, Severity

_IGNORED_VALUES = frozenset({0, 1, 2, -1})
_USAGE_COMPARISONS = "comparaciones"
_USAGE_OPERATIONS = "operaciones"
_USAGE_BOTH = "comparaciones y operaciones"
_USAGE_FILE = "el archivo"
_HIGH_SEVERITY_OCCURRENCES = 3


@dataclass(frozen=True)
class _Occurrence:
    value: int | float
    node: ast.AST
    line: int
    column: int
    in_compare: bool
    in_arith: bool


def _numeric_constant(node: ast.AST) -> ast.Constant | None:
    if not isinstance(node, ast.Constant):
        return None
    if isinstance(node.value, bool):
        return None
    if not isinstance(node.value, (int, float)):
        return None
    return node


def _literal_value(
    node: ast.AST, parents: dict[ast.AST, ast.AST]
) -> tuple[ast.AST, int | float] | None:
    if isinstance(node, ast.Constant):
        if _numeric_constant(node) is None:
            return None
        parent = parents.get(node)
        if isinstance(parent, ast.UnaryOp) and isinstance(parent.op, ast.USub):
            return None
        return node, node.value
    if not isinstance(node, ast.UnaryOp) or not isinstance(node.op, ast.USub):
        return None
    operand = _numeric_constant(node.operand)
    if operand is None:
        return None
    return node, -operand.value


def _is_named_constant(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> bool:
    parent = parents.get(node)
    if isinstance(parent, ast.Assign):
        targets = parent.targets
    elif isinstance(parent, ast.AnnAssign):
        targets = [parent.target]
    else:
        return False
    if parent.value is not node or len(targets) != 1:
        return False
    target = targets[0]
    return isinstance(target, ast.Name) and target.id.isupper()


def _context_flags(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> tuple[bool, bool]:
    in_compare = False
    in_arith = False
    current = parents.get(node)
    while current is not None:
        if isinstance(current, ast.Compare):
            in_compare = True
        elif is_arithmetic(current):
            in_arith = True
        current = parents.get(current)
    return in_compare, in_arith


def _occurrences(
    tree: ast.Module, parents: dict[ast.AST, ast.AST]
) -> list[_Occurrence]:
    occurrences: list[_Occurrence] = []
    for node in ast.walk(tree):
        resolved = _literal_value(node, parents)
        if resolved is None:
            continue
        literal, value = resolved
        if value in _IGNORED_VALUES:
            continue
        if _is_named_constant(literal, parents):
            continue
        in_compare, in_arith = _context_flags(literal, parents)
        occurrences.append(
            _Occurrence(
                value=value,
                node=literal,
                line=literal.lineno,
                column=literal.col_offset,
                in_compare=in_compare,
                in_arith=in_arith,
            )
        )
    return occurrences


def _usage(occurrences: list[_Occurrence]) -> str:
    has_compare = any(occurrence.in_compare for occurrence in occurrences)
    has_arith = any(occurrence.in_arith for occurrence in occurrences)
    if has_compare and has_arith:
        return _USAGE_BOTH
    if has_compare:
        return _USAGE_COMPARISONS
    if has_arith:
        return _USAGE_OPERATIONS
    return _USAGE_FILE


def _unique_lines(occurrences: list[_Occurrence]) -> list[int]:
    return list(dict.fromkeys(occurrence.line for occurrence in occurrences))


def _is_magic(occurrences: list[_Occurrence], min_occurrences: int) -> bool:
    if len(occurrences) >= min_occurrences:
        return True
    return any(
        occurrence.in_compare or occurrence.in_arith
        for occurrence in occurrences
    )


def _group_by_value(
    occurrences: list[_Occurrence],
) -> dict[int | float, list[_Occurrence]]:
    groups: dict[int | float, list[_Occurrence]] = {}
    for occurrence in occurrences:
        groups.setdefault(occurrence.value, []).append(occurrence)
    return groups


class MagicNumberDetector:
    code = "D2"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        parents = parent_map(ctx.tree)
        groups = _group_by_value(_occurrences(ctx.tree, parents))
        detections: list[Detection] = []
        for occurrences in groups.values():
            ordered = sorted(
                occurrences, key=lambda occurrence: (occurrence.line, occurrence.column)
            )
            if not _is_magic(ordered, ctx.config.magic_min_occurrences):
                continue
            first = ordered[0]
            detections.append(
                Detection(
                    code=self.code,
                    line=first.line,
                    column=first.column,
                    severity=(
                        Severity.ALTA
                        if len(ordered) >= _HIGH_SEVERITY_OCCURRENCES
                        else Severity.MEDIA
                    ),
                    context={
                        "value": ctx.segment(first.node, limit=20),
                        "count": len(ordered),
                        "lines": _unique_lines(ordered),
                        "usage": _usage(ordered),
                    },
                )
            )
        detections.sort(key=lambda detection: (detection.line, detection.column))
        return detections[: ctx.config.max_findings_per_detector]
