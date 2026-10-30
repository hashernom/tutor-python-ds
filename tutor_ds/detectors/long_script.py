import ast

from tutor_ds.ast_utils import script_statement_count
from tutor_ds.models import AnalysisContext, Detection, Severity

_TOP_LEVEL_DEFINITIONS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


class LongScriptDetector:
    code = "D4"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        statements = script_statement_count(ctx.tree)
        if statements < ctx.config.long_script_min_statements:
            return []
        if any(
            isinstance(statement, _TOP_LEVEL_DEFINITIONS)
            for statement in ctx.tree.body
        ):
            return []
        severity = (
            Severity.ALTA
            if statements >= ctx.config.long_script_high_statements
            else Severity.MEDIA
        )
        return [
            Detection(
                code=self.code,
                line=1,
                column=0,
                context={"statements": statements},
                severity=severity,
            )
        ]
