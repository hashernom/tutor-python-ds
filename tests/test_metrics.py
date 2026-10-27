from tutor_ds.loader import build_context
from tutor_ds.metrics import compute_metrics


def test_metrics_count_top_level_functions_classes_and_methods():
    src = "import math\n\ndef area(r):\n    if r > 0:\n        return math.pi * r ** 2\n    return 0.0\n\nclass Factura:\n    def total(self, base):\n        return base * 1.19\n"
    ctx = build_context(src)
    metrics = compute_metrics(ctx.tree, ctx.lines)
    assert metrics.function_count == 1
    assert metrics.method_count == 1
    assert metrics.class_count == 1
    assert metrics.top_level_statements == 3
    assert metrics.max_nesting_depth == 1
    assert metrics.io_call_count == 0
