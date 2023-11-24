import numpy as np

from drmeter.compat import calc_drscore
from drmeter.utils import ignore_div0
from tests.fixtures import FIXTURES_DIR, parametrize_fixtures


def mean_across_channels(vals: np.ndarray) -> np.ndarray:
    lin_mean = np.power(10, vals / 20).mean()
    with ignore_div0():
        return 20 * np.log10(lin_mean)


def max_across_channels(vals: np.ndarray) -> np.ndarray:
    lin_mean = np.power(10, vals / 20).max()
    with ignore_div0():
        return 20 * np.log10(lin_mean)


@parametrize_fixtures
def test_compat_calc_drscore(filename: str, expected_score: float, expected_peak: float, expected_rms: float) -> None:
    result = calc_drscore(FIXTURES_DIR / filename)

    assert round(result[0].mean()) == expected_score
    assert max_across_channels(result[1]) == expected_peak
    assert mean_across_channels(result[2]) == expected_rms
