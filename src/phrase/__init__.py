from importlib.metadata import PackageNotFoundError, version

try:  # noqa: RUF067
    __version__ = version("phrase")  # use version info from `pyproject.toml`
except PackageNotFoundError:
    __version__ = "unknown"  # The package is not installed.

__all__ = ["__version__"]
