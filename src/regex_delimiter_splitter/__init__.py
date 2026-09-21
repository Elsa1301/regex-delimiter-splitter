"""Regex Delimiter Splitter.

Split strings on regex patterns while keeping track of match positions and
captured groups.
"""

from .core import split_with_delimiters

__all__ = ["split_with_delimiters"]
