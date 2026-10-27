import ast

from tutor_ds.ast_utils import (
    function_params,
    is_io_call,
    iter_functions,
    script_statement_count,
)
from tutor_ds.loader import build_context


def _calls(source):
    tree = build_context(source).tree
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call)]


def test_is_io_call_accepts_print_input_and_sys_write():
    assert all(is_io_call(c) for c in _calls("print(1)\nx = input()\nsys.stdout.write('a')\n"))


def test_is_io_call_rejects_domain_functions():
    assert not any(is_io_call(c) for c in _calls("print_total(x)\ncalculadora.imprimir(x)\n"))


def test_function_params_exclude_self_and_variadics():
    tree = build_context("class A:\n    def m(self, x, *args, y=1, **kw):\n        pass\n").tree
    fn = next(iter_functions(tree))
    assert function_params(fn) == ("x", "y")


def test_script_statement_count_walks_control_flow_but_not_definitions():
    src = '"""doc"""\nimport os\nif cond:\n    a = 1\n    b = 2\ndef f():\n    c = 3\n'
    assert script_statement_count(build_context(src).tree) == 3
