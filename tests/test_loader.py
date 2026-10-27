import pytest

from tutor_ds.loader import build_context


def test_build_context_raises_syntax_error():
    with pytest.raises(SyntaxError):
        build_context("def (:\n")
