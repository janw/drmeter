from __future__ import annotations

from typing import TYPE_CHECKING

from drmeter.algorithm import dynamic_range
from drmeter.models import AudioData

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np


def calc_drscore(filename: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    result = dynamic_range(AudioData.from_filename(filename))

    return result.dr_score, result.peak_db, result.rms_db
