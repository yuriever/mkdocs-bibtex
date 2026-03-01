import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mkdocs_bibtex.utils import extract_cite_keys, find_cite_blocks


class TestCiteBlocks(unittest.TestCase):
    def test_matches_simple_cite(self):
        markdown = r"Text with \cite{author} cite"
        self.assertEqual(find_cite_blocks(markdown), [r"\cite{author}"])

    def test_matches_cite_with_note(self):
        markdown = r"Text with \cite[Section 2]{author} cite"
        self.assertEqual(find_cite_blocks(markdown), [r"\cite[Section 2]{author}"])

    def test_does_not_merge_adjacent_cites_with_text_between(self):
        markdown = r"\cite{author}, xxxx \cite{author2}"
        self.assertEqual(find_cite_blocks(markdown), [r"\cite{author}", r"\cite{author2}"])

    def test_does_not_match_non_cite_commands(self):
        markdown = r"\parencite{author}"
        self.assertEqual(find_cite_blocks(markdown), [])

    def test_does_not_match_legacy_pandoc_citation(self):
        markdown = "[@author]"
        self.assertEqual(find_cite_blocks(markdown), [])

    def test_extract_cite_key_for_simple_cite(self):
        self.assertEqual(extract_cite_keys(r"\cite{author}"), ["author"])

    def test_extract_cite_key_for_cite_with_note(self):
        self.assertEqual(extract_cite_keys(r"\cite[p. 123]{author}"), ["author"])

    def test_extract_cite_keys_for_multi_cite(self):
        self.assertEqual(extract_cite_keys(r"\cite{author1,author2}"), ["author1", "author2"])

    def test_spacing_variants_match_and_extract(self):
        variants = [
            r"\cite{a,b}",
            r"\cite{a, b}",
            r"\cite{ a ,  b }",
            r"\cite [Sec. 2] { a , b }",
        ]
        for v in variants:
            self.assertEqual(find_cite_blocks(v), [v])
            self.assertEqual(extract_cite_keys(v), ["a", "b"])

    def test_multi_cite_with_note(self):
        s = r"\cite[p. 2]{a,b}"
        self.assertEqual(find_cite_blocks(s), [s])
        self.assertEqual(extract_cite_keys(s), ["a", "b"])

    def test_extract_cite_keys_with_internal_blanks(self):
        block = r"\cite{author one, author two}"
        self.assertEqual(find_cite_blocks(block), [block])
        self.assertEqual(extract_cite_keys(block), ["author one", "author two"])

    def test_extract_returns_empty_for_invalid_block(self):
        self.assertEqual(extract_cite_keys(r"\cite{author"), [])

    def test_does_not_match_malformed_option_block(self):
        markdown = r"\cite[Section 2{author}"
        self.assertEqual(find_cite_blocks(markdown), [])


if __name__ == "__main__":
    unittest.main()
