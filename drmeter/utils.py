from __future__ import annotations

import math
from contextlib import contextmanager
from typing import Generator

import numpy as np
import soundfile as sf
from rich.box import Box
from rich.console import Console
from rich.spinner import Spinner
from rich.table import Table


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


def print_formats(console: Console) -> None:
    table = Table(show_header=True, header_style="bold magenta", box=rich_box)
    table.add_column("Extension")
    table.add_column("Description")
    for fmt, description in sf.available_formats().items():
        table.add_row(fmt, description)
    console.print(table)
