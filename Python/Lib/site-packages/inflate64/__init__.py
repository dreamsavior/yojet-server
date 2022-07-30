from importlib.metadata import PackageNotFoundError, version

from ._inflate64 import Inflater  # noqa

__all__ = Inflater

__doc__ = """\
Python library to inflate data, the API is similar to Python's bz2/lzma/zlib module.
"""

__copyright__ = "Copyright (C) 2022 Hiroshi Miura"

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no-cover
    # package is not installed
    __version__ = "0.1.0"
