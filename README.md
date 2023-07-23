# Dynamic Range (DR) meter 🎧


<!-- markdownlint-disable MD033 MD013 -->
<div align="center">

[![Tests](https://github.com/janw/drmeter/actions/workflows/tests.yaml/badge.svg)](https://github.com/janw/drmeter/actions/workflows/tests.yaml)
[![Coverage Status](https://codecov.io/gh/janw/drmeter/branch/main/graph/badge.svg?token=N8DBXQTM74)](https://codecov.io/gh/janw/drmeter)

[![PyPI](https://img.shields.io/pypi/v/drmeter.svg)](https://pypi.org/project/drmeter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/drmeter.svg)](https://pypi.org/project/drmeter/)
[![Downloads](https://static.pepy.tech/badge/drmeter)](https://pepy.tech/project/drmeter)

[![Linter: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v1.json)](https://github.com/charliermarsh/ruff)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Dependency management: poetry](https://img.shields.io/badge/deps-poetry-blueviolet.svg)](https://poetry.eustace.io/docs/)

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

## Usage

See `drmeter --help` for usage instructions.

## Example output

TBD
