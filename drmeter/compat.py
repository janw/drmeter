from __future__ import annotations

from typing import TYPE_CHECKING

import soundfile as sf

from drmeter.algorithm import dynamic_range
from drmeter.models import AudioData

if TYPE_CHECKING:
    from pathlib import Path

    import numpy as np


def calc_drscore(filename: str | Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with sf.SoundFile(filename) as soundfile:
        result = dynamic_range(AudioData.from_soundfile(soundfile))

    return result.dr_score, result.peak_db, result.rms_db
