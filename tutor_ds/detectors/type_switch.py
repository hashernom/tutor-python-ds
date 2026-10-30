import ast
from dataclasses import dataclass

from tutor_ds.ast_utils import normalize_expr, parent_map
from tutor_ds.models import AnalysisContext, Detection, Severity

_COMPARISON_OPS = (ast.Eq, ast.NotEq, ast.In, ast.NotIn)
_ISINSTANCE_NAME = "isinstance"
_NUMERIC_TYPES = (int, float, complex)


@dataclass(frozen=True)
class _Branch:
    discriminant: str
    values: tuple[str, ...]


def _is_chain_head(node: ast.If, parents: dict[ast.AST, ast.AST]) -> bool:
    parent = parents.get(node)
    if isinstance(parent, ast.If) and len(parent.orelse) == 1:
        return parent.orelse[0] is not node
    return True


def _is_numeric_constant(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Constant)
        and isinstance(node.value, _NUMERIC_TYPES)
        and not isinstance(node.value, bool)
    )


def _literal_text(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant):
        return normalize_expr(node)
    if (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and _is_numeric_constant(node.operand)
    ):
        return normalize_expr(node)
    return None


def _comparator_values(node: ast.AST) -> tuple[str, ...] | None:
    text = _literal_text(node)
    if text is not None:
        return (text,)
    if not isinstance(node, (ast.Tuple, ast.List)):
        return None
    values: list[str] = []
    for element in node.elts:
        element_text = _literal_text(element)
        if element_text is not None:
            values.append(element_text)
    return tuple(values) if values else None


def _isinstance_values(node: ast.AST) -> tuple[str, tuple[str, ...]] | None:
    if not isinstance(node, ast.Call) or node.keywords:
        return None
    if not isinstance(node.func, ast.Name) or node.func.id != _ISINSTANCE_NAME:
        return None
    if len(node.args) < 2:
        return None
    return normalize_expr(node.args[0]), (normalize_expr(node.args[1]),)


def _branch(node: ast.If) -> _Branch | None:
    test = node.test
    if isinstance(test, ast.Compare):
        if len(test.ops) != 1 or len(test.comparators) != 1:
            return None
        if not isinstance(test.ops[0], _COMPARISON_OPS):
            return None
        values = _comparator_values(test.comparators[0])
        if values is None:
            return None
        return _Branch(normalize_expr(test.left), values)
    resolved = _isinstance_values(test)
    if resolved is None:
        return None
    return _Branch(*resolved)


def _chain_branches(head: ast.If) -> list[_Branch]:
    branches: list[_Branch] = []
    current = head
    while True:
        branch = _branch(current)
        if branch is not None:
            branches.append(branch)
        if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
            current = current.orelse[0]
            continue
        return branches


def _select_discriminant(
    branches: list[_Branch], min_branches: int
) -> tuple[str, int] | None:
    counts: dict[str, int] = {}
    for branch in branches:
        counts[branch.discriminant] = counts.get(branch.discriminant, 0) + 1
    for branch in branches:
        count = counts[branch.discriminant]
        if count >= min_branches:
            return branch.discriminant, count
    return None


def _chain_values(branches: list[_Branch], discriminant: str) -> list[str]:
    values: list[str] = []
    for branch in branches:
        if branch.discriminant == discriminant:
            values.extend(branch.values)
    return values


class TypeSwitchDetector:
    code = "D5"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        parents = parent_map(ctx.tree)
        heads = sorted(
            (
                node
                for node in ast.walk(ctx.tree)
                if isinstance(node, ast.If) and _is_chain_head(node, parents)
            ),
            key=lambda node: (node.lineno, node.col_offset),
        )
        detections: list[Detection] = []
        for head in heads:
            branches = _chain_branches(head)
            selected = _select_discriminant(
                branches, ctx.config.type_switch_min_branches
            )
            if selected is None:
                continue
            variable, branch_count = selected
            detections.append(
                Detection(
                    code=self.code,
                    line=head.lineno,
                    column=head.col_offset,
                    context={
                        "variable": variable,
                        "branches": branch_count,
                        "values": _chain_values(branches, variable),
                    },
                    severity=(
                        Severity.ALTA
                        if branch_count >= ctx.config.type_switch_high_branches
                        else Severity.MEDIA
                    ),
                )
            )
            if len(detections) >= ctx.config.max_findings_per_detector:
                break
        return detections
