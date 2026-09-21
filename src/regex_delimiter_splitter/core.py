"""Core implementation for regex delimiter splitting."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Pattern, Sequence, Union


@dataclass(frozen=True)
class DelimiterMatch:
    """A regex delimiter match found while splitting.

    Attributes:
        start: Index in the original string where the delimiter match starts.
        end: Index in the original string where the delimiter match ends.
        text: The matched delimiter substring.
        groups: A tuple containing all captured groups from the match. Empty
            groups are represented as None, matching re.Match.groups()
            semantics.
    """

    start: int
    end: int
    text: str
    groups: tuple


@dataclass(frozen=True)
class SplitResult:
    """Result of splitting a string with a regex delimiter.

    Attributes:
        parts: The non-delimiter substrings between delimiters. Consecutive
            delimiters produce empty strings in this list, mirroring
            str.split() when given an explicit separator. A trailing delimiter
            produces a final empty string.
        delimiters: The DelimiterMatch objects for each delimiter that was
            found, in order of occurrence.
        original: The original input string.
    """

    parts: List[str]
    delimiters: List[DelimiterMatch]
    original: str

    @property
    def positions(self) -> List[Optional[int]]:
        """Return start positions of each delimiter match.

        Useful for callers that only need locations, not groups.
        """
        return [dm.start for dm in self.delimiters]


_DEFAULT_FLAGS = 0


def split_with_delimiters(
    text: str,
    pattern: Union[str, Pattern[str]],
    flags: int = _DEFAULT_FLAGS,
    *,
    maxsplit: int = -1,
) -> SplitResult:
    """Split text using a regex delimiter, retaining match details.

    This function behaves like re.split(), but instead of embedding captured
    groups in the output, it returns them separately alongside position
    information for each delimiter match.

    The splitting algorithm matches the behaviour of re.split() for the
    common case where the pattern has no capturing groups: the text is split
    on every non-overlapping occurrence of the pattern, and consecutive
    delimiters produce empty parts. When the pattern does contain capturing
    groups, the groups are recorded in the DelimiterMatch objects rather than
    being interleaved into the parts list, which keeps parts as the pure
    non-delimiter substrings.

    Args:
        text: The string to split.
        pattern: A regex pattern as a string or compiled re.Pattern.
        flags: Regex flags to apply if pattern is a string. Ignored if pattern
            is already compiled.
        maxsplit: Maximum number of splits to perform. The default -1 means
            no limit. A value of 0 returns the entire text as a single part
            with no delimiters. Negative values other than -1 are treated as
            -1.

    Returns:
        A SplitResult containing the non-delimiter parts, the delimiter
        matches, and the original text.

    Raises:
        re.error: If the pattern is invalid.
        TypeError: If text is not a string or pattern is not a string or
            compiled regex.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if isinstance(pattern, str):
        compiled = re.compile(pattern, flags)
    elif isinstance(pattern, re.Pattern):
        compiled = pattern
    else:
        raise TypeError("pattern must be a string or compiled re.Pattern")

    if maxsplit == 0:
        return SplitResult(parts=[text], delimiters=[], original=text)

    # Normalise negative maxsplit values to -1 (unlimited).
    effective_maxsplit = -1 if maxsplit < 0 else maxsplit

    parts: List[str] = []
    delimiters: List[DelimiterMatch] = []
    last_end = 0
    splits_done = 0

    for match in compiled.finditer(text):
        if effective_maxsplit != -1 and splits_done >= effective_maxsplit:
            break

        parts.append(text[last_end : match.start()])
        delimiters.append(
            DelimiterMatch(
                start=match.start(),
                end=match.end(),
                text=match.group(0),
                groups=match.groups(),
            )
        )
        last_end = match.end()
        splits_done += 1

    parts.append(text[last_end:])

    return SplitResult(parts=parts, delimiters=delimiters, original=text)
