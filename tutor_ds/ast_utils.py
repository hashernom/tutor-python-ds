import ast
from collections.abc import Iterator

IO_BUILTIN_NAMES = frozenset({"print", "input", "open"})
IO_METHOD_NAMES = frozenset({"write", "read", "readline"})
IO_ROOT_NAME = "sys"

ARITHMETIC_OPS: frozenset[type[ast.operator]] = frozenset(
    {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow}
)

CONTROL_FLOW_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.Match)
SCOPE_NODES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
EXCLUDED_PARAM_NAMES = frozenset({"self", "cls"})


def _root_name(node: ast.AST) -> str | None:
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def is_io_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in IO_BUILTIN_NAMES
    if isinstance(func, ast.Attribute):
        return func.attr in IO_METHOD_NAMES and _root_name(func) == IO_ROOT_NAME
    return False


def is_arithmetic(node: ast.AST) -> bool:
    return isinstance(node, ast.BinOp) and type(node.op) in ARITHMETIC_OPS


def normalize_expr(node: ast.AST) -> str:
    return ast.unparse(node)


def parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    return {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }


def iter_functions(
    tree: ast.AST,
) -> Iterator[ast.FunctionDef | ast.AsyncFunctionDef]:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def function_params(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, ...]:
    arguments = node.args
    ordered = (*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs)
    return tuple(
        argument.arg
        for argument in ordered
        if argument.arg not in EXCLUDED_PARAM_NAMES
    )


def _is_docstring(statement: ast.stmt) -> bool:
    return (
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Constant)
        and isinstance(statement.value.value, str)
    )


def _body_statements(statement: ast.stmt) -> Iterator[ast.stmt]:
    if isinstance(statement, ast.If):
        yield from statement.body
        yield from statement.orelse
    elif isinstance(statement, (ast.For, ast.While)):
        yield from statement.body
        yield from statement.orelse
    elif isinstance(statement, ast.With):
        yield from statement.body
    elif isinstance(statement, ast.Try):
        yield from statement.body
        yield from statement.orelse
        yield from statement.finalbody
        for handler in statement.handlers:
            yield from handler.body
    elif isinstance(statement, ast.Match):
        for case in statement.cases:
            yield from case.body


def _count_statement(statement: ast.stmt) -> int:
    if isinstance(statement, (ast.Import, ast.ImportFrom, *SCOPE_NODES)):
        return 0
    if isinstance(statement, CONTROL_FLOW_NODES):
        return 1 + sum(_count_statement(child) for child in _body_statements(statement))
    return 1


def script_statement_count(tree: ast.Module) -> int:
    total = 0
    for index, statement in enumerate(tree.body):
        if index == 0 and _is_docstring(statement):
            continue
        total += _count_statement(statement)
    return total
