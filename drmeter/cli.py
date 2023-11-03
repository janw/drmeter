from __future__ import annotations

import pathlib
from contextlib import nullcontext
from typing import Callable, TypeVar

import rich_click as click
from rich.console import Console
from rich.live import Live
from rich.text import Text

from drmeter import __name__ as pkg_name
from drmeter import __version__
from drmeter.algorithm import SUPPORTED_EXTENSIONS
from drmeter.models import AnalysisList
from drmeter.utils import fmt_dr_score, print_formats

T = TypeVar("T")


def required_without_formats(ctx: click.Context, param: click.Parameter, value: T) -> T:
    if not ctx.params.get("formats", False) and value is None:
        raise click.MissingParameter
    return value


def mutually_exclusive_flag(*exclusives: str) -> Callable:
    def _mutually_exclusive(ctx: click.Context, param: click.Parameter, value: T) -> T:
        assert param.name
        for excl in exclusives:
            if ctx.params.get(excl, False) is True and value is True:
                raise click.BadOptionUsage(
                    param.name,
                    f"Option '--{param.name}' and '--{excl}' are mutually exclusive.",
                    ctx=ctx,
                )
        return value

    return _mutually_exclusive


click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True


@click.command(
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
)
@click.argument(
    "filepath",
    type=click.Path(
        exists=True,
        readable=True,
        file_okay=True,
        dir_okay=True,
    ),
    required=False,
    callback=required_without_formats,
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["json"]),
    help="Select a specific output format.",
)
@click.option(
    "-F",
    "--formats",
    is_flag=True,
    help="Show a list of supported formats and exit.",
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Emit debug-level messages about the analysis.",
    callback=mutually_exclusive_flag("quiet"),
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help=("Don't emit non-error messages. " "Errors are still emitted; silence those with 2>/dev/null."),
    callback=mutually_exclusive_flag("debug"),
)
@click.version_option(
    __version__,
    "-V",
    "--version",
    prog_name=pkg_name,
)
def main(
    filepath: str | pathlib.Path,
    formats: bool = False,
    quiet: bool = False,
    debug: bool = False,
    output: str | None = None,
) -> int:
    """
    Dynamic Range (DR) analyzer for audiofiles.

    Given a filename or directory, the tool will analyze the supported files for their
    dynamic range (DR). For a list of supported formats, use the --formats flag.

    Lower DR values are an indicator for a more liberal use of dynamic compression and
    limiting in the music production process that can be detrimental to the audio
    quality of the recording, resulting in a squashed sound that can be fatiguing to
    listen to.

    Higher values generally imply a higher audio quality and details being more
    perceivable. There is no such thing as "best dynamic range", and there are many more
    aspects of a recording that influence its perceived quality. Dynamic Range (as
    calculated by this tool) is merely a tool to become more aware of the differences,
    and ultimately end the [loudness war](https://en.wikipedia.org/wiki/Loudness_war).
    """
    console = Console(quiet=quiet, stderr=bool(output))
    if debug:
        click.echo("Debug mode is on")

    if isinstance(filepath, str):
        filepath = pathlib.Path(filepath)

    if formats:
        print_formats(console)
        return 0

    if filepath.is_dir():
        text = Text.assemble(
            "Analyzing Dynamic Range of files in ",
            (str(filepath), "bold magenta"),
            " ...\n",
        )
        files = sorted(f for f in filepath.glob("*") if f.suffix in SUPPORTED_EXTENSIONS)
    else:
        text = Text.assemble(
            "Analyzing Dynamic Range of ",
            (str(filepath), "bold magenta"),
            " ...\n",
        )
        files = [filepath]

    console.print(text)
    results = AnalysisList.from_paths(files)
    live_ctx = nullcontext() if debug else Live(results, console=console, refresh_per_second=15)
    with live_ctx:  # type: ignore[attr-defined]
        results.analyze(debug=debug, live=not quiet)

    assert results.overall_result
    content = None
    if output == "json":
        content = results.to_json()
    elif quiet:
        content = fmt_dr_score(results.overall_result.overall_dr_score)

    if content:
        click.echo(content)

    return 0
