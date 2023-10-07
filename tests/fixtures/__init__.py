import json
from functools import cache
from pathlib import Path
from typing import cast

import pytest

FIXTURES_DIR = Path(__file__).parent
FIXTURES_INFO_FILE = "_fixtures.json"


DEFAULT_ABS_TOL_DR = 5e-1
DEFAULT_ABS_TOL_PEAK = 1e-2
DEFAULT_ABS_TOL_RMS = 1e-2


@cache
def load_fixtures() -> list[tuple[str, float, float, float]]:
    with (FIXTURES_DIR / FIXTURES_INFO_FILE).open() as fixtures_file:
        fixtures_list = json.load(fixtures_file)

    return [
        (
            cast(str, f["filename"]),
            cast(float, pytest.approx(f["expected_score"], abs=DEFAULT_ABS_TOL_DR)),
            cast(float, pytest.approx(f["expected_peak"], abs=DEFAULT_ABS_TOL_PEAK)),
            cast(float, pytest.approx(f["expected_rms"], abs=DEFAULT_ABS_TOL_RMS)),
        )
        for f in fixtures_list
    ]


parametrize_fixtures = pytest.mark.parametrize(
    "filename, expected_score, expected_peak, expected_rms", load_fixtures()
)
