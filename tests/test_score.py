import numpy as np
import pytest
import soundfile as sf

from drmeter.algorithm import dynamic_range
from drmeter.exceptions import FileTooShort
from drmeter.models import AudioData
from tests.fixtures import FIXTURES_DIR, parametrize_fixtures


@parametrize_fixtures
def test_score_for_fixture(
    filename: str, expected_score: float, expected_peak: float, expected_rms: float
) -> None:
    with sf.SoundFile(FIXTURES_DIR / filename) as data:
        result = dynamic_range(AudioData.from_soundfile(data))

    assert result.overall_rms_db == expected_rms
    assert result.overall_peak_db == expected_peak
    assert result.overall_dr_score == expected_score


def test_error_too_short() -> None:
    data = AudioData(
        data=np.zeros((100, 1)),
        samplerate=8000,
        channels=1,
        frames=100,
    )
    with pytest.raises(FileTooShort):
        dynamic_range(data)


def test_from_np_array() -> None:
    data = AudioData(
        data=np.zeros((8000 * 15, 1)),
        samplerate=8000,
        channels=1,
        frames=8000 * 15,
    )
    result = dynamic_range(data)

    assert result.dr_score[0] == 0
