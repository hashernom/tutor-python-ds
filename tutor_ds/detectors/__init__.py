from tutor_ds.detectors.base import Detector
from tutor_ds.detectors.data_clumps import DataClumpDetector
from tutor_ds.detectors.duplication import DuplicationDetector
from tutor_ds.detectors.io_mixing import IoMixingDetector
from tutor_ds.detectors.long_script import LongScriptDetector
from tutor_ds.detectors.magic_numbers import MagicNumberDetector
from tutor_ds.detectors.type_switch import TypeSwitchDetector
from tutor_ds.models import AnalysisContext, Detection

DETECTORS: tuple[Detector, ...] = (
    IoMixingDetector(),
    MagicNumberDetector(),
    DuplicationDetector(),
    LongScriptDetector(),
    TypeSwitchDetector(),
    DataClumpDetector(),
)


def run_detectors(ctx: AnalysisContext) -> list[Detection]:
    detections: list[Detection] = []
    for detector in DETECTORS:
        detections.extend(detector.detect(ctx))
    return detections
