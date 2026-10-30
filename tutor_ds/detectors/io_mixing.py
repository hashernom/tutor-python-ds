import ast
from collections.abc import Iterator

from tutor_ds.ast_utils import is_arithmetic, is_io_call, parent_map
from tutor_ds.models import AnalysisContext, Detection

_SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _iter_scope_nodes(statements: list[ast.stmt]) -> Iterator[ast.AST]:
    stack = list(reversed(statements))
    while stack:
        node = stack.pop()
        if isinstance(node, _SCOPE_NODES):
            continue
        yield node
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _is_inside_io_call(
    node: ast.AST, parents: dict[ast.AST, ast.AST]
) -> bool:
    current = parents.get(node)
    while current is not None:
        if is_io_call(current):
            return True
        current = parents.get(current)
    return False


def _io_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ast.unparse(func)


def _functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    found = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    return sorted(found, key=lambda node: (node.lineno, node.col_offset))


class IoMixingDetector:
    code = "D1"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        parents = parent_map(ctx.tree)
        detections: list[Detection] = []
        scopes: list[tuple[str, str, list[ast.stmt]]] = [
            ("módulo", "módulo", ctx.tree.body)
        ]
        scopes.extend(
            ("función", function.name, function.body)
            for function in _functions(ctx.tree)
        )
        for scope_kind, scope_name, statements in scopes:
            first_io: ast.Call | None = None
            first_calculation: ast.BinOp | None = None
            for node in _iter_scope_nodes(statements):
                if first_io is None and is_io_call(node):
                    first_io = node
                elif (
                    first_calculation is None
                    and is_arithmetic(node)
                    and not _is_inside_io_call(node, parents)
                ):
                    first_calculation = node
                if first_io is not None and first_calculation is not None:
                    break
            if first_io is None or first_calculation is None:
                continue
            detections.append(
                Detection(
                    code=self.code,
                    line=first_io.lineno,
                    column=first_io.col_offset,
                    context={
                        "scope_kind": scope_kind,
                        "scope": scope_name,
                        "calculation": ctx.segment(first_calculation),
                        "io": _io_name(first_io),
                    },
                )
            )
            if len(detections) >= ctx.config.max_findings_per_detector:
                break
        return detections
