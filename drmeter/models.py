from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

import numpy as np
import soundfile as sf
from rich.table import Table

from drmeter.utils import fmt_dr_score, rich_box, rich_spinner, to_decibels

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderableType


@dataclass
class DynamicRangeResult:
    dr_score: np.ndarray | float
    peak_pressure: np.ndarray | float = field(repr=False)
    rms_pressure: np.ndarray | float = field(repr=False)

    peak_db: np.ndarray | float = field(repr=False, init=False)
    rms_db: np.ndarray | float = field(repr=False, init=False)

    total_dr_score: float = field(repr=False, init=False)
    total_peak_pressure: float = field(repr=False, init=False)
    total_rms_pressure: float = field(repr=False, init=False)

    total_peak_db: float = field(init=False)
    total_rms_db: float = field(init=False)

    def __post_init__(self) -> None:
        self.total_dr_score = (
            self.dr_score.mean()
            if isinstance(self.dr_score, np.ndarray)
            else self.dr_score
        )
        self.total_peak_pressure = (
            self.peak_pressure.max()
            if isinstance(self.peak_pressure, np.ndarray)
            else self.peak_pressure
        )
        self.total_rms_pressure = (
            self.rms_pressure.mean()
            if isinstance(self.rms_pressure, np.ndarray)
            else self.rms_pressure
        )
        self.total_peak_db = to_decibels(self.total_peak_pressure)
        self.total_rms_db = to_decibels(self.total_rms_pressure)


@dataclass
class AnalysisItem:
    path: Path
    result: DynamicRangeResult | None = None

    def analyze(self) -> None:
        from drmeter.algorithm import dynamic_range

        with sf.SoundFile(self.path) as soundfile:
            self.result = dynamic_range(soundfile)

    def rich_table_render(self) -> tuple[RenderableType, ...]:
        if not self.result:
            return (rich_spinner, rich_spinner, rich_spinner, self.path.name)
        return (
            fmt_dr_score(self.result.total_dr_score),
            f"{self.result.total_peak_db:+6.2f} dB",
            f"{self.result.total_rms_db:+6.2f} dB",
            self.path.name,
        )


@dataclass
class AnalysisList:
    results: dict[Path, AnalysisItem] = field(default_factory=dict)

    overall_result: DynamicRangeResult | None = None

    _table: Table | None = None
    _directory: Path | None = None
    _overall_count: int = 0

    def __len__(self) -> int:
        return len(self.results)

    @classmethod
    def from_paths(cls, paths: list[Path]) -> AnalysisList:
        return cls(results={path: AnalysisItem(path=path) for path in paths})

    def analyze(self) -> None:
        def analyze_and_update(result: AnalysisItem) -> None:
            result.analyze()
            self.calculate_overall_result()
            self.generate_table()

        with ThreadPoolExecutor() as pool:
            for result in self.results.values():
                pool.submit(analyze_and_update, result)

    def generate_table(self) -> None:
        self._table = Table(show_header=True, header_style="bold magenta", box=rich_box)
        self._table.add_column("DR", width=5)
        self._table.add_column("Peak", justify="right", width=10)
        self._table.add_column("RMS", justify="right", width=10)
        self._table.add_column("Filename")
        for _, result in sorted(self.results.items()):
            self._table.add_row(*result.rich_table_render())

        if len(self.results) < 2:
            return

        self._table.add_section()
        desc = f"Overall ({self._overall_count} file{'s' if self._overall_count !=1 else ''})"
        style = "bold magenta"
        if self.overall_result and self._overall_count:
            self._table.add_row(
                fmt_dr_score(self.overall_result.total_dr_score),
                f"{self.overall_result.total_peak_db:+6.2f} dB",
                f"{self.overall_result.total_rms_db:+6.2f} dB",
                desc,
                style=style,
            )
        else:
            self._table.add_row(
                rich_spinner, rich_spinner, rich_spinner, desc, style=style
            )

    def calculate_overall_result(self) -> None:
        result_count = 0

        dr_score = 0.0
        peak_pressure = 0.0
        rms_pressure = 0.0
        for result in self.results.values():
            if not result.result:
                continue

            dr_score += result.result.total_dr_score
            peak_pressure = max(result.result.total_peak_pressure, peak_pressure)
            rms_pressure += result.result.total_rms_pressure
            result_count += 1

        if result_count > 0:
            self.overall_result = DynamicRangeResult(
                dr_score=dr_score / result_count,
                peak_pressure=peak_pressure,
                rms_pressure=rms_pressure / result_count,
            )
            self._overall_count = result_count

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> Iterable[Table]:
        if not self._table:
            self.generate_table()
        assert self._table
        yield self._table
