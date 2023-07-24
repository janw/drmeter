from __future__ import annotations

import math
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, TypeVar

import numpy as np
import soundfile as sf
from rich.box import Box
from rich.console import Console
from rich.spinner import Spinner
from rich.table import Table

V = TypeVar("V", np.ndarray, float)

OUTPUT_ROUNDING_DECIMALS = 2


@contextmanager
def ignore_div0() -> Generator[None, None, None]:
    _np_errs = np.seterr(divide="ignore")
    yield
    np.seterr(**_np_errs)


def to_decibels(val: V) -> V:
    if isinstance(val, float):
        if val == 0:
            return -math.inf
        return 20 * math.log10(val)
    with ignore_div0():
        return 20 * np.log10(val)


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


def serialize(obj: Any) -> Any:
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = serialize(value)
    elif isinstance(obj, (tuple, list)):
        obj = [serialize(val) for val in obj]
    elif isinstance(obj, np.ndarray):
        return serialize(np.round(obj, decimals=OUTPUT_ROUNDING_DECIMALS).tolist())
    elif isinstance(obj, float):
        if math.isinf(obj):
            return None
        return round(obj, ndigits=OUTPUT_ROUNDING_DECIMALS)
    elif isinstance(obj, Path):
        return str(obj.absolute())
    return obj
