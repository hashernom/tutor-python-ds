import ast

from tutor_ds.ast_utils import is_io_call, iter_functions, parent_map
from tutor_ds.models import SourceMetrics

CONTROL_FLOW_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.Match)


def max_nesting_depth(tree: ast.AST) -> int:
    deepest = 0

    def visit(node: ast.AST, depth: int) -> None:
        nonlocal deepest
        if isinstance(node, CONTROL_FLOW_NODES):
            depth += 1
            if depth > deepest:
                deepest = depth
        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree, 0)
    return deepest


def compute_metrics(tree: ast.Module, lines: tuple[str, ...]) -> SourceMetrics:
    parents = parent_map(tree)
    functions = tuple(iter_functions(tree))
    return SourceMetrics(
        line_count=len(lines),
        function_count=sum(
            1 for node in functions if isinstance(parents.get(node), ast.Module)
        ),
        class_count=sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef)),
        method_count=sum(
            1 for node in functions if isinstance(parents.get(node), ast.ClassDef)
        ),
        top_level_statements=len(tree.body),
        max_nesting_depth=max_nesting_depth(tree),
        io_call_count=sum(1 for node in ast.walk(tree) if is_io_call(node)),
    )
