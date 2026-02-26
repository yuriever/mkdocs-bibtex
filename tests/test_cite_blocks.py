import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mkdocs_bibtex.utils import extract_cite_keys, find_cite_blocks


class TestCiteBlocks(unittest.TestCase):
    def test_matches_simple_cite(self):
        markdown = "Text with [@author] cite"
        self.assertEqual(find_cite_blocks(markdown), ["[@author]"])

    def test_matches_cite_with_suffix(self):
        markdown = "Text with [@author, p. 123] cite"
        self.assertEqual(find_cite_blocks(markdown), ["[@author, p. 123]"])

    def test_does_not_merge_adjacent_cites_with_text_between(self):
        markdown = "[@author], xxxx [@author2]"
        self.assertEqual(find_cite_blocks(markdown), ["[@author]", "[@author2]"])

    def test_does_not_match_negative_author_form(self):
        markdown = "[-@author]"
        self.assertEqual(find_cite_blocks(markdown), [])

    def test_does_not_match_multi_cite_semicolon_form(self):
        markdown = "[@author; @doe]"
        self.assertEqual(find_cite_blocks(markdown), ["[@author; @doe]"])

    def test_extract_cite_key_for_simple_cite(self):
        self.assertEqual(extract_cite_keys("[@author]"), ["author"])

    def test_extract_cite_key_for_cite_with_suffix(self):
        self.assertEqual(extract_cite_keys("[@author, p. 123]"), ["author"])

    def test_extract_cite_keys_for_multi_cite(self):
        self.assertEqual(extract_cite_keys("[@author; @doe]"), ["author", "doe"])

    def test_spacing_variants_match_and_extract(self):
        variants = ["[@a;@b]", "[@a ; @b]", "[@a;  @b]"]
        for v in variants:
            self.assertEqual(find_cite_blocks(v), [v])
            self.assertEqual(extract_cite_keys(v), ["a", "b"])

    def test_multi_cite_with_suffix(self):
        s = "[@a; @b, p. 2]"
        self.assertEqual(find_cite_blocks(s), [s])
        self.assertEqual(extract_cite_keys(s), ["a", "b"])

    def test_complex_colon_and_semicolon_keys(self):
        block = "[@author1:1000xx; @author1:2000xx; @author2:1000xx; @author2:2000xx]"
        expected_keys = [
            "author1:1000xx",
            "author1:2000xx",
            "author2:1000xx",
            "author2:2000xx",
        ]
        self.assertEqual(find_cite_blocks(block), [block])
        self.assertEqual(extract_cite_keys(block), expected_keys)

    def test_extract_returns_empty_for_invalid_block(self):
        self.assertEqual(extract_cite_keys("[-@author]"), [])


if __name__ == "__main__":
    unittest.main()
