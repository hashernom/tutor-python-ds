from typing import Protocol

from tutor_ds.models import AnalysisContext, Detection


class Detector(Protocol):
    code: str

    def detect(self, ctx: AnalysisContext) -> list[Detection]: ...
