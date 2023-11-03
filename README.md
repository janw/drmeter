# Dynamic Range (DR) meter 🎧


<!-- markdownlint-disable MD033 MD013 -->
<div align="center">

[![Tests](https://github.com/janw/drmeter/actions/workflows/tests.yaml/badge.svg)](https://github.com/janw/drmeter/actions/workflows/tests.yaml)
[![Coverage Status](https://codecov.io/gh/janw/drmeter/branch/main/graph/badge.svg?token=N8DBXQTM74)](https://codecov.io/gh/janw/drmeter)
[![Docker](https://github.com/janw/drmeter/actions/workflows/docker.yaml/badge.svg)](https://github.com/janw/drmeter/pkgs/container/drmeter)

[![PyPI](https://img.shields.io/pypi/v/drmeter.svg)](https://pypi.org/project/drmeter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drmeter.svg)](https://pypi.org/project/drmeter/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/drmeter)

[![Linter/Formatter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://black.readthedocs.io/en/stable/)
[![Dependency management: poetry](https://img.shields.io/badge/deps-poetry-blueviolet.svg)](https://python-poetry.org/docs/)

<p>A Dynamic Range (DR) analyzer for audiofiles.<p>

<a href="https://asciinema.org/a/598647" target="_blank"><img alt="Asciicast of installing and using drmeter" src="https://asciinema.org/a/598647.svg" /></a>
</div>

The algorithm has been reverse-engineered using the available information and officially endorsed software to calcuate the DR value. The analysis results of `drmeter` are verified to be within a ±0.5 absolute tolerance from the results produced by officially endorsed software (see #testing).

This project is in no way affiliated with the Pleasurize Music Foundation or its Dynamic Range Project.

## Installation

The recommended method for installing `drmeter` is [pipx](https://pypa.github.io/pipx/):

```bash
pipx install drmeter
```

Any regular `pip install drmeter` will do, too. The `drmeter` requires Python 3.9+ to run.

To use `drmeter` without installation, consider the [dockerized approach](#dockerized) below

## Usage

See `drmeter --help` for usage instructions. `drmeter` expects a single path to a file or a directory to analyze, and defaults to an "animated" progress display, emitting the results to stdout in the process.

```sh
$ drmeter 'Nobody There (Beautiful Scars).wav'
Analyzing Dynamic Range of Nobody There (Beautiful Scars).wav ...

╭──────────────────────────────────────────────────────────────────────╮
│ DR            Peak          RMS   Filename                           │
├──────────────────────────────────────────────────────────────────────┤
│ DR12      -0.10 dB    -15.02 dB   Nobody There (Beautiful Scars).wav │
╰──────────────────────────────────────────────────────────────────────╯
```

Using the `--quiet/-q` flag will silence most of the output and only print the calculated DR score to stdout:

```sh
$ drmeter 'Nobody There (Beautiful Scars).wav' -q
DR12
```

Alternatively `drmeter` supports a more detailed JSON-formatted output using the `--output/-o json` parameter, including both per-channel and totaled results. Using the `--output` parameter redirects the progress display to stderr, so that the formatted output can be piped to other applications or to file. If you do not require the progress display, it can be silenced using `--quiet/-q` here, too.

```sh
# Save a copy to file
$ drmeter -ojson -q 'Nobody There (Beautiful Scars).wav' | tee dr.json
{
  "filename": "/…/Nobody There (Beautiful Scars).wav",
  "dr_score": [
    11.93,
    11.63
  ],
  "peak_db": [
    …
  ]
}
```

```sh
# Parse JSON using jq
$ drmeter -ojson -q 'Nobody There (Beautiful Scars).wav' | jq '.[].overall_dr_score'
11.78
```

### Dockerized

A container image of `drmeter` is available at `ghcr.io/janw/drmeter` with the `latest` tag pointing to the latest commit on the `main` branch. The following command (with the files you're looking to analyze in/below the current working directory) behaves very similarly to an installed version, accepting arguments directly as expected:

```sh
docker run --rm --tty --workdir /src -v "$PWD:/src" \
    ghcr.io/janw/drmeter --output json path/to/files
```
