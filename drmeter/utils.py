from __future__ import annotations

import math
from contextlib import contextmanager
from typing import Generator

import numpy as np
from rich.box import Box
from rich.spinner import Spinner
from rich.table import Table


def create_rich_table() -> Table:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("DR")
    table.add_column("Peak", justify="right")
    table.add_column("RMS", justify="right")
    table.add_column("Filename")
    return table


@contextmanager
def ignore_div0() -> Generator[None, None, None]:
    _np_errs = np.seterr(divide="ignore")
    yield
    np.seterr(**_np_errs)


def to_decibels(val: float) -> float:
    if val == 0:
        return -math.inf
    return 20 * math.log10(val)


def fmt_dr_score(val: float) -> str:
    return f"DR{val:.0f}"


rich_box = Box(
    """\
╭──╮
│  │
├──┤
│  │
├──┤
├──┤
│  │
╰──╯
"""
)

rich_spinner = Spinner("dots")
