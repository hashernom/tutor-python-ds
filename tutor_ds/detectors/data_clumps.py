from dataclasses import dataclass
from itertools import combinations

from tutor_ds.ast_utils import function_params, iter_functions
from tutor_ds.models import AnalysisContext, Detection


@dataclass(frozen=True)
class _Function:
    name: str
    line: int
    column: int
    params: frozenset[str]


class DataClumpDetector:
    code = "D6"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        functions = [
            _Function(
                name=node.name,
                line=node.lineno,
                column=node.col_offset,
                params=frozenset(function_params(node)),
            )
            for node in iter_functions(ctx.tree)
        ]
        names: dict[frozenset[str], set[str]] = {}
        positions: dict[frozenset[str], tuple[int, int]] = {}
        for first, second in combinations(functions, 2):
            shared = first.params & second.params
            if len(shared) < ctx.config.data_clump_min_params:
                continue
            names.setdefault(shared, set()).update((first.name, second.name))
            position = min(
                (first.line, first.column), (second.line, second.column)
            )
            current = positions.get(shared)
            if current is None or position < current:
                positions[shared] = position
        reported = [
            key for key in names if not any(key < other for other in names)
        ]
        ordered = sorted(reported, key=lambda key: (-len(key), sorted(key)))
        detections: list[Detection] = []
        for key in ordered:
            if len(detections) >= ctx.config.max_findings_per_detector:
                break
            line, column = positions[key]
            detections.append(
                Detection(
                    code=self.code,
                    line=line,
                    column=column,
                    context={
                        "params": sorted(key),
                        "functions": sorted(names[key]),
                    },
                )
            )
        return detections
