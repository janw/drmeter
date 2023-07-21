from __future__ import annotations

import argparse
from pathlib import Path

import soundfile as sf
from rich.console import Console
from rich.live import Live

from drmeter.algorithm import SUPPORTED_EXTENSIONS
from drmeter.models import AnalysisList


def filename_or_directory_arg(value: str) -> Path:
    path = Path(value)
    if path.is_dir() or path.is_file():
        return path
    raise ValueError(f"Filename or directory '{value}' does not exist")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filename_or_directory",
        metavar="FILENAME_OR_DIRECTORY",
        type=filename_or_directory_arg,
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
    )
    parser.add_argument(
        "--list-formats",
        action="store_true",
    )
    args = parser.parse_args(argv)

    if args.list_formats:
        for fmt, description in sf.available_formats().items():
            print(f"{fmt:8s} : {description}")
        return 0

    console = Console(quiet=args.quiet)
    path = args.filename_or_directory
    if path.is_dir():
        console.print(f"Analyzing Dynamic Range of files in {path} ...")
        files = sorted(f for f in path.glob("*") if f.suffix in SUPPORTED_EXTENSIONS)
    else:
        console.print(f"Analyzing Dynamic Range of {path} ...")
        files = [path]

    results = AnalysisList.from_paths(files)
    with Live(results, console=console, refresh_per_second=15):  # type: ignore[attr-defined]
        results.analyze()

    return 0
