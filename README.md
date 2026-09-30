# Regex Delimiter Splitter

Splits strings on regex patterns while keeping track of match positions and captured groups.

## Usage

```python
from regex_delimiter_splitter import split_with_delimiters

result = split_with_delimiters("key:123,other:456", r"(\w+):(\d+)")

print(result.parts)       # ['', ',', '']
print(result.delimiters)  # [DelimiterMatch(start=0, end=7, text='key:123', groups=('key', '123')), ...]
print(result.positions)   # [0, 8]
```

The function returns a `SplitResult` with three fields:

- `parts`: list of non-delimiter substrings, in order. Consecutive delimiters produce empty strings, and a trailing delimiter produces a final empty string.
- `delimiters`: list of `DelimiterMatch` objects, each containing `start`, `end`, `text`, and `groups` for one delimiter match.
- `original`: the input string.

`positions` is a convenience property that returns the start index of each delimiter match.

`pattern` may be a regex string or a compiled `re.Pattern`. If a string is given, `flags` are passed to `re.compile`. The `maxsplit` keyword works like `re.split`: 0 returns the entire text as one part, negative values mean unlimited.

## Why this exists

Python's `re.split` can keep captured groups, but it interleaves them with the parts and discards position information. When you need to know where each delimiter was found, or to process parts and delimiters separately, you end up writing the same loop over `finditer` every time. This library packages that loop once.

The main trade-off is that captured groups are moved out of the parts list and into the delimiter records. That keeps `parts` as pure non-delimiter text, but it means callers who relied on `re.split`'s interleaved-group behaviour will need to consult `delimiters` instead.

## Edge cases

An empty regex pattern `""` matches at every position, including the start and end of the string. The result for `"abc"` is `parts=['', 'a', 'b', 'c', '']` with three zero-width delimiter matches. This matches `re.split` semantics and is intentional, but can surprise callers expecting a no-op.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

