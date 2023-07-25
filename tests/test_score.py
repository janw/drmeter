from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

from drmeter.algorithm import dynamic_range

FIXTURES_DIR = Path(__file__).parent / "fixtures"

DEFAULT_ABS_TOL_DR = 5e-1
DEFAULT_ABS_TOL_PEAK = 1e-2
DEFAULT_ABS_TOL_RMS = 1e-2


@pytest.mark.parametrize(
    "filename, expected_score, expected_peak, expected_rms",
    [
        (
            "silence.wav",
            0,
            -np.inf,
            -np.inf,
        ),
        (
            "csd_en001b.mp3",
            pytest.approx(10, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(-8.38, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-22.24, abs=DEFAULT_ABS_TOL_RMS),
        ),
        (
            "csd_kr032b.mp3",
            pytest.approx(11, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(-5.64, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-22.42, abs=DEFAULT_ABS_TOL_RMS),
        ),
        (
            "tee_falcon69_mixture.mp3",
            pytest.approx(12, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(0.01, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-13.69, abs=DEFAULT_ABS_TOL_RMS),
        ),
        (
            "tee_sdnr_bass.mp3",
            pytest.approx(11, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(-6.72, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-21.72, abs=DEFAULT_ABS_TOL_RMS),
        ),
        (
            "tee_sdnr_mix.mp3",
            pytest.approx(12, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(-1.33, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-16.06, abs=DEFAULT_ABS_TOL_RMS),
        ),
        (
            "tee_sdnr_vocals.mp3",
            pytest.approx(11, abs=DEFAULT_ABS_TOL_DR),
            pytest.approx(-5.16, abs=DEFAULT_ABS_TOL_PEAK),
            pytest.approx(-19.80, abs=DEFAULT_ABS_TOL_RMS),
        ),
    ],
)
def test_score_for_fixture(
    filename: str, expected_score: float, expected_peak: float, expected_rms: float
) -> None:
    with sf.SoundFile(FIXTURES_DIR / filename) as data:
        result = dynamic_range(data)

    assert result.overall_rms_db == expected_rms
    assert result.overall_peak_db == expected_peak
    assert result.overall_dr_score == expected_score
