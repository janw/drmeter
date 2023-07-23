import importlib.metadata as importlib_metadata

from drmeter.algorithm import dynamic_range

__all__ = [
    "dynamic_range",
]

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "dev"
