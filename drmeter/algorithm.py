from __future__ import annotations

import math

import numpy as np
import soundfile as sf

from drmeter.exceptions import FileTooShort
from drmeter.models import AudioData, DynamicRangeResult
from drmeter.utils import ignore_div0

BLOCKSIZE_SECONDS = 3
UPMOST_BLOCKS_RATIO = 0.2
NTH_HIGHEST_PEAK = 2

MIN_BLOCK_COUNT = 1 // UPMOST_BLOCKS_RATIO
MIN_DURATION = MIN_BLOCK_COUNT * BLOCKSIZE_SECONDS

SUPPORTED_EXTENSIONS = {f".{fmt.lower()}" for fmt in sf.available_formats()}


def _analyze_block_levels(
    data: sf.SoundFile,
    total_blocks: int,
    blocksize: int,
) -> tuple[np.ndarray, np.ndarray]:
    block_rms = np.zeros((total_blocks, data.channels))
    block_peak = np.zeros((total_blocks, data.channels))
    for nn, block in enumerate(data.blocks(blocksize=blocksize)):
        interim = 2 * (np.power(np.abs(block), 2))
        block_rms[nn] = np.sqrt(interim.mean(axis=0, keepdims=True))
        block_peak[nn] = np.abs(block).max(axis=0)

    block_rms.sort(axis=0)
    block_peak.sort(axis=0)
    return block_rms, block_peak


def dynamic_range(data: AudioData) -> DynamicRangeResult:
    blocksize = round(BLOCKSIZE_SECONDS * data.samplerate)
    total_blocks = math.ceil(data.frames / blocksize)
    if total_blocks < MIN_BLOCK_COUNT:
        raise FileTooShort(f"File cannot be shorter than {MIN_DURATION} seconds")

    block_rms, block_peak = _analyze_block_levels(data, total_blocks=total_blocks, blocksize=blocksize)
    with ignore_div0():
        rms_pressure = np.sqrt((np.power(block_rms, 2)).mean(axis=0))
        peak_pressure = block_peak[-1]

    upmost_blocks = round(total_blocks * UPMOST_BLOCKS_RATIO)
    upmost_blocks_rms = block_rms[-upmost_blocks:]
    pre0 = np.power(upmost_blocks_rms, 2).sum(axis=0)
    pre1 = np.repeat(upmost_blocks, data.channels, axis=0)
    pre2 = np.sqrt(pre0 / pre1)

    dr_score: np.ndarray = np.array(
        [
            20 * np.log10(_peak / _pre2) if _pre2 > 0 else 0.0
            for _peak, _pre2 in zip(block_peak[-NTH_HIGHEST_PEAK], pre2)
        ]
    )

    return DynamicRangeResult(dr_score=dr_score, peak_pressure=peak_pressure, rms_pressure=rms_pressure)
