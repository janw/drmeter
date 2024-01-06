from __future__ import annotations

import math

import numpy as np

from drmeter.exceptions import FileTooShort
from drmeter.models import AudioData, DynamicRangeResult
from drmeter.utils import ignore_div0

BLOCKSIZE_SECONDS = 3
UPMOST_BLOCKS_RATIO = 0.2
NTH_HIGHEST_PEAK = 2

MIN_BLOCK_COUNT = 1 // UPMOST_BLOCKS_RATIO
MIN_DURATION = MIN_BLOCK_COUNT * BLOCKSIZE_SECONDS


LOW_THRESHOLD = -100  # dB


def _analyze_block_levels(
    data: AudioData,
    total_blocks: int,
    blocksize: int,
) -> tuple[np.ndarray, np.ndarray]:
    block_rms = np.zeros((data.channels, total_blocks))
    block_peaks = np.zeros((data.channels, total_blocks))
    multiplier = 2 / blocksize
    for nn, block in enumerate(data.blocks(blocksize=blocksize)):
        block_rms[:, nn] = np.sqrt(multiplier * (np.sum(np.power(np.abs(block), 2), axis=1)))
        block_peaks[:, nn] = np.abs(block).max(axis=1)

    return block_rms, block_peaks


def dynamic_range(data: AudioData) -> DynamicRangeResult:
    blocksize = round(BLOCKSIZE_SECONDS * data.samplerate)
    total_blocks = math.ceil(data.frames / blocksize)
    upmost_blocks = round(total_blocks * UPMOST_BLOCKS_RATIO)

    if total_blocks < MIN_BLOCK_COUNT:
        raise FileTooShort(f"File cannot be shorter than {MIN_DURATION} seconds")

    block_rms, block_peaks = _analyze_block_levels(data, total_blocks=total_blocks, blocksize=blocksize)

    rms_rounded = np.sort((20 * np.log10(block_rms)).round(decimals=2))
    upmost_rms_db = rms_rounded[:, -upmost_blocks:]
    upmost_rms_lin = np.power(10, upmost_rms_db / 20)

    peaks_rounded = np.sort(np.unique((20 * np.log10(block_peaks)).round(decimals=2), axis=1))
    overall_peak_db = peaks_rounded[:, -1]
    overall_peak_lin = np.power(10, overall_peak_db / 20)

    if peaks_rounded.shape[1] < 2:
        peaks_rounded = np.insert(peaks_rounded, 0, peaks_rounded, axis=1)
    overall_2nd_peak_db = peaks_rounded[:, -2]
    overall_2nd_peak_lin = np.power(10, overall_2nd_peak_db / 20)

    with ignore_div0():
        upmost_rms_sum_lin = np.sqrt(np.power(upmost_rms_lin, 2).sum(axis=1) / upmost_blocks)
        rms_mean_total = np.sqrt((np.power(block_rms, 2)).sum(axis=1) / total_blocks)

        dr_score: np.ndarray = np.nan_to_num(
            -20 * np.log10(upmost_rms_sum_lin / overall_2nd_peak_lin),
            nan=0.0,
        )

    return DynamicRangeResult(dr_score=dr_score, peak_pressure=overall_peak_lin, rms_pressure=rms_mean_total)
