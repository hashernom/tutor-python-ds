import ast
from collections.abc import Iterator

from tutor_ds.models import AnalysisContext, Detection

_CONTAINER_NODES = (
    ast.Module,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.If,
    ast.For,
    ast.While,
    ast.With,
    ast.Try,
)
_BLOCK_FIELDS = ("body", "orelse", "finalbody")


def _iter_blocks(tree: ast.Module) -> Iterator[list[ast.stmt]]:
    for node in ast.walk(tree):
        if isinstance(node, _CONTAINER_NODES):
            for field in _BLOCK_FIELDS:
                block = getattr(node, field, None)
                if isinstance(block, list) and block:
                    yield block
        elif isinstance(node, ast.ExceptHandler) and node.body:
            yield node.body


def _fingerprint(block: list[ast.stmt]) -> str:
    return "\n".join(
        ast.dump(statement, annotate_fields=False, include_attributes=False)
        for statement in block
    )


def _block_size(block: list[ast.stmt]) -> int:
    return sum(1 for statement in block for _ in ast.walk(statement))


def _block_nodes(block: list[ast.stmt]) -> Iterator[ast.AST]:
    for statement in block:
        yield from ast.walk(statement)


def _first_line(block: list[ast.stmt]) -> int:
    return block[0].lineno


def _groups(
    blocks: Iterator[list[ast.stmt]],
) -> dict[str, list[list[ast.stmt]]]:
    groups: dict[str, list[list[ast.stmt]]] = {}
    for block in blocks:
        groups.setdefault(_fingerprint(block), []).append(block)
    return groups


class DuplicationDetector:
    code = "D3"

    def detect(self, ctx: AnalysisContext) -> list[Detection]:
        candidates: list[tuple[int, list[list[ast.stmt]]]] = []
        for blocks in _groups(_iter_blocks(ctx.tree)).values():
            if len(blocks) < 2:
                continue
            size = _block_size(blocks[0])
            if size < ctx.config.duplicate_min_nodes:
                continue
            candidates.append((size, blocks))
        candidates.sort(
            key=lambda candidate: (
                -candidate[0],
                min(_first_line(block) for block in candidate[1]),
            )
        )
        covered: set[int] = set()
        detections: list[Detection] = []
        for size, blocks in candidates:
            ordered = sorted(blocks, key=_first_line)
            nodes = [node for block in ordered for node in _block_nodes(block)]
            if all(id(node) in covered for node in nodes):
                continue
            covered.update(id(node) for node in nodes)
            first = ordered[0][0]
            detections.append(
                Detection(
                    code=self.code,
                    line=first.lineno,
                    column=first.col_offset,
                    context={
                        "count": len(ordered),
                        "lines": [_first_line(block) for block in ordered],
                        "nodes": size,
                        "snippet": ctx.segment(first, limit=80),
                    },
                )
            )
        detections.sort(key=lambda detection: (detection.line, detection.column))
        return detections[: ctx.config.max_findings_per_detector]
