import importlib.metadata as importlib_metadata

from drmeter.algorithm import dynamic_range
from drmeter.compat import calc_drscore

__all__ = [
    "calc_drscore",
    "dynamic_range",
]

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"
