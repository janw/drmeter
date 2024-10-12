from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, Iterator

import numpy as np
import soundfile as sf
from rich.table import Table

from drmeter.utils import (
    fmt_dr_score,
    rich_box,
    rich_spinner,
    serialize,
    to_decibels,
)

if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderableType


@dataclass
class AudioData:
    data: sf.SoundFile | np.ndarray
    samplerate: int
    channels: int
    frames: int

    def blocks(self, blocksize: int) -> Iterator[np.ndarray]:
        if isinstance(self.data, sf.SoundFile):
            yield from self.data.blocks(blocksize=blocksize)
            return
        idx = 0
        while len(block := self.data[idx:blocksize]) > 0:
            yield block
            idx += blocksize

    @classmethod
    def from_soundfile(cls, soundfile: sf.SoundFile) -> AudioData:
        return cls(
            data=soundfile,
            channels=soundfile.channels,
            frames=soundfile.frames,
            samplerate=soundfile.samplerate,
        )


@dataclass
class DynamicRangeResult:
    dr_score: np.ndarray
    peak_pressure: np.ndarray = field(repr=False)
    rms_pressure: np.ndarray = field(repr=False)

    peak_db: np.ndarray = field(repr=False, init=False)
    rms_db: np.ndarray = field(repr=False, init=False)

    overall_dr_score: float = field(repr=False, init=False)
    overall_peak_pressure: float = field(repr=False, init=False)
    overall_rms_pressure: float = field(repr=False, init=False)

    overall_peak_db: float = field(init=False)
    overall_rms_db: float = field(init=False)

    def __post_init__(self) -> None:
        self.overall_dr_score = self.dr_score.mean() if isinstance(self.dr_score, np.ndarray) else self.dr_score
        self.overall_peak_pressure = (
            self.peak_pressure.max() if isinstance(self.peak_pressure, np.ndarray) else self.peak_pressure
        )
        self.overall_rms_pressure = (
            self.rms_pressure.mean() if isinstance(self.rms_pressure, np.ndarray) else self.rms_pressure
        )
        self.peak_db = to_decibels(self.peak_pressure)  # type: ignore[type-var]
        self.rms_db = to_decibels(self.rms_pressure)  # type: ignore[type-var]
        self.overall_peak_db = to_decibels(self.overall_peak_pressure)
        self.overall_rms_db = to_decibels(self.overall_rms_pressure)


@dataclass
class AnalysisItem:
    path: Path
    result: DynamicRangeResult | None = None

    def analyze(self) -> None:
        from drmeter.algorithm import dynamic_range

        with sf.SoundFile(self.path) as soundfile:
            self.result = dynamic_range(AudioData.from_soundfile(soundfile))

    def rich_table_render(self) -> tuple[RenderableType, ...]:
        if not self.result:
            return (rich_spinner, rich_spinner, rich_spinner, self.path.name)
        return (
            fmt_dr_score(self.result.overall_dr_score),
            f"{self.result.overall_peak_db:+6.2f} dB",
            f"{self.result.overall_rms_db:+6.2f} dB",
            self.path.name,
        )

    def to_dict(self) -> dict[str, Any]:
        data = {"filename": str(self.path.absolute())}
        if not self.result:
            return data

        obj = asdict(self.result)
        del obj["peak_pressure"]
        del obj["rms_pressure"]
        del obj["overall_peak_pressure"]
        del obj["overall_rms_pressure"]
        data.update(serialize(obj))
        return data


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

    def analyze(self, debug: bool = False, live: bool = False) -> None:
        if debug:
            import click

            for path, result in self.results.items():
                click.echo(f"Analyzing {path} ...")
                result.analyze()
        else:

            def analyze_and_update(result: AnalysisItem) -> None:
                result.analyze()
                if live:
                    self.calculate_overall_result()
                    self.generate_table()

            with ThreadPoolExecutor() as pool:
                for result in self.results.values():
                    pool.submit(analyze_and_update, result)

        self.calculate_overall_result()

    def to_json(self) -> str:
        results = [item.to_dict() for item in self.results.values() if item.result]
        return json.dumps(results, indent=2)

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
                fmt_dr_score(self.overall_result.overall_dr_score),
                f"{self.overall_result.overall_peak_db:+6.2f} dB",
                f"{self.overall_result.overall_rms_db:+6.2f} dB",
                desc,
                style=style,
            )
        else:
            self._table.add_row(rich_spinner, rich_spinner, rich_spinner, desc, style=style)

    def calculate_overall_result(self) -> None:
        result_count = 0

        dr_score = 0.0
        peak_pressure = 0.0
        rms_pressure = 0.0
        for result in self.results.values():
            if not result.result:
                continue

            dr_score += result.result.overall_dr_score
            peak_pressure = max(result.result.overall_peak_pressure, peak_pressure)
            rms_pressure += result.result.overall_rms_pressure
            result_count += 1

        if result_count > 0:
            self.overall_result = DynamicRangeResult(
                dr_score=np.array([dr_score / result_count]),
                peak_pressure=np.array([peak_pressure]),
                rms_pressure=np.array([rms_pressure / result_count]),
            )
            self._overall_count = result_count

    def __rich_console__(self, console: Console, options: ConsoleOptions) -> Iterable[Table]:
        if not self._table:
            self.generate_table()
        assert self._table
        yield self._table
