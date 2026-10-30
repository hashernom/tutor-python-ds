from tutor_ds.detectors.base import Detector
from tutor_ds.detectors.io_mixing import IoMixingDetector
from tutor_ds.models import AnalysisContext, Detection

DETECTORS: tuple[Detector, ...] = (IoMixingDetector(),)


def run_detectors(ctx: AnalysisContext) -> list[Detection]:
    detections: list[Detection] = []
    for detector in DETECTORS:
        detections.extend(detector.detect(ctx))
    return detections
