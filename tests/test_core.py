"""Tests for regex_delimiter_splitter.core."""

import re
import unittest

from regex_delimiter_splitter import split_with_delimiters
from regex_delimiter_splitter.core import DelimiterMatch, SplitResult


class SplitWithDelimitersTests(unittest.TestCase):
    def test_simple_delimiter(self):
        result = split_with_delimiters("a,b,c", ",")
        self.assertEqual(result.parts, ["a", "b", "c"])
        self.assertEqual(len(result.delimiters), 2)
        self.assertEqual(result.delimiters[0].start, 1)
        self.assertEqual(result.delimiters[0].end, 2)
        self.assertEqual(result.delimiters[0].text, ",")
        self.assertEqual(result.delimiters[0].groups, ())
        self.assertEqual(result.delimiters[1].start, 3)
        self.assertEqual(result.original, "a,b,c")

    def test_no_delimiters(self):
        result = split_with_delimiters("hello", ",")
        self.assertEqual(result.parts, ["hello"])
        self.assertEqual(result.delimiters, [])
        self.assertEqual(result.original, "hello")

    def test_consecutive_delimiters(self):
        result = split_with_delimiters("a,,b", ",")
        self.assertEqual(result.parts, ["a", "", "b"])
        self.assertEqual(len(result.delimiters), 2)

    def test_trailing_delimiter(self):
        result = split_with_delimiters("a,b,", ",")
        self.assertEqual(result.parts, ["a", "b", ""])
        self.assertEqual(len(result.delimiters), 2)

    def test_leading_delimiter(self):
        result = split_with_delimiters(",a,b", ",")
        self.assertEqual(result.parts, ["", "a", "b"])
        self.assertEqual(len(result.delimiters), 2)

    def test_maxsplit(self):
        result = split_with_delimiters("a,b,c,d", ",", maxsplit=2)
        self.assertEqual(result.parts, ["a", "b", "c,d"])
        self.assertEqual(len(result.delimiters), 2)

    def test_maxsplit_zero(self):
        result = split_with_delimiters("a,b,c", ",", maxsplit=0)
        self.assertEqual(result.parts, ["a,b,c"])
        self.assertEqual(result.delimiters, [])

    def test_negative_maxsplit(self):
        result = split_with_delimiters("a,b,c", ",", maxsplit=-5)
        self.assertEqual(result.parts, ["a", "b", "c"])
        self.assertEqual(len(result.delimiters), 2)

    def test_capturing_groups_recorded(self):
        pattern = r"(\d+)-(\w+)"
        result = split_with_delimiters("x12-ab y", pattern)
        self.assertEqual(result.parts, ["x", " y"])
        self.assertEqual(len(result.delimiters), 1)
        dm = result.delimiters[0]
        self.assertEqual(dm.text, "12-ab")
        self.assertEqual(dm.groups, ("12", "ab"))
        self.assertEqual(dm.start, 1)
        self.assertEqual(dm.end, 6)

    def test_pattern_with_no_group_returns_empty_tuple(self):
        result = split_with_delimiters("a|b", r"\|")
        self.assertEqual(result.parts, ["a", "b"])
        self.assertEqual(result.delimiters[0].groups, ())

    def test_compiled_pattern(self):
        compiled = re.compile(r"\s+")
        result = split_with_delimiters("a  b\tc", compiled)
        self.assertEqual(result.parts, ["a", "b", "c"])
        self.assertEqual(len(result.delimiters), 2)
        self.assertEqual(result.delimiters[0].text, "  ")
        self.assertEqual(result.delimiters[1].text, "\t")

    def test_flags_applied_to_string_pattern(self):
        result = split_with_delimiters("aXbxc", "x", flags=re.IGNORECASE)
        self.assertEqual(result.parts, ["a", "b", "c"])
        self.assertEqual(len(result.delimiters), 2)

    def test_positions_property(self):
        result = split_with_delimiters("one,two,three", ",")
        self.assertEqual(result.positions, [3, 7])

    def test_type_error_text(self):
        with self.assertRaises(TypeError):
            split_with_delimiters(123, ",")

    def test_type_error_pattern(self):
        with self.assertRaises(TypeError):
            split_with_delimiters("abc", 123)

    def test_invalid_regex_raises(self):
        with self.assertRaises(re.error):
            split_with_delimiters("abc", "(")

    def test_empty_pattern_splits_between_characters(self):
        result = split_with_delimiters("abc", "")
        self.assertEqual(result.parts, ["", "a", "b", "c", ""])
        self.assertEqual(len(result.delimiters), 4)
        self.assertEqual(result.delimiters[0].start, 0)
        self.assertEqual(result.delimiters[0].end, 0)
        self.assertEqual(result.delimiters[1].start, 1)
        self.assertEqual(result.delimiters[1].end, 1)

    def test_empty_text(self):
        result = split_with_delimiters("", ",")
        self.assertEqual(result.parts, [""])
        self.assertEqual(result.delimiters, [])

    def test_result_types(self):
        result = split_with_delimiters("a,b", ",")
        self.assertIsInstance(result, SplitResult)
        self.assertIsInstance(result.delimiters[0], DelimiterMatch)


if __name__ == "__main__":
    unittest.main()
