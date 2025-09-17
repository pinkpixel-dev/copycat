"""CopyCat clipboard utility package."""

from importlib.metadata import version, PackageNotFoundError

__all__ = [
    "__version__",
]

try:
    __version__ = version("copycat-clipboard")
except PackageNotFoundError:  # pragma: no cover - fallback for local usage
__version__ = "1.0.1"
