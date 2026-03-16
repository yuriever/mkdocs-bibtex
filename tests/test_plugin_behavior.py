import os
import sys
import tempfile
import unittest
from pathlib import Path

import markdown as md

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mkdocs_bibtex.plugin import BibTeXPlugin


class DummyConfig(dict):
    def __init__(self, config_file_path: str):
        super().__init__(config_file_path=config_file_path)
        self.config_file_path = config_file_path


class TestPluginBehavior(unittest.TestCase):
    def _render_html(self, plugin, markdown, config):
        processed_markdown = plugin.on_page_markdown(
            markdown,
            page=None,
            config=config,
            files=None,
        )
        return md.markdown(processed_markdown, extensions=["footnotes"])

    def _write_sample_bib(self, path: Path):
        path.write_text(
            """@article{smith2020,
  title={Example Title},
  author={Smith, John},
  journal={Example Journal},
  year={2020}
}
@article{doe2021,
  title={Another Title},
  author={Doe, Jane},
  journal={Another Journal},
  year={2021}
}
@article{lee2022,
    title={Third Title},
    author={Lee, Alex},
    journal={Third Journal},
    year={2022}
}
@article{kim2023,
    title={Fourth Title},
    author={Kim, Sam},
    journal={Fourth Journal},
    year={2023}
}
@article{patel2024,
    title={Fifth Title},
    author={Patel, Priya},
    journal={Fifth Journal},
    year={2024}
}
""",
            encoding="utf-8",
        )

    def _make_plugin(self, bib_dir: str) -> BibTeXPlugin:
        plugin = BibTeXPlugin()
        plugin.config = {
            "bib_dir": bib_dir,
            "footnote_format": "{number}",
            "bib_by_default": True,
            "bib_command": "\\bibliography",
            "full_bib_command": "\\full_bibliography",
        }
        return plugin

    def test_loads_entries_from_bib_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            self.assertIn("smith2020", plugin.bib_data.entries)

    def test_resolves_relative_bib_dir_from_mkdocs_config_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            mkdocs_file = docs_dir / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin("../bibliography")
            config = DummyConfig(str(mkdocs_file))

            old_cwd = os.getcwd()
            try:
                os.chdir("/")
                plugin.on_config(config)
            finally:
                os.chdir(old_cwd)

            self.assertIn("smith2020", plugin.bib_data.entries)

    def test_requires_bib_dir(self):
        plugin = BibTeXPlugin()
        plugin.config = {
            "footnote_format": "{number}",
            "bib_by_default": True,
            "bib_command": "\\bibliography",
            "full_bib_command": "\\full_bibliography",
        }
        config = DummyConfig("/tmp/mkdocs.yml")

        with self.assertRaises(Exception) as exc_info:
            plugin.on_config(config)

        self.assertIn("bib_dir", str(exc_info.exception))

    def test_warns_unknown_key_once_per_build(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            with self.assertLogs("mkdocs.plugins.mkdocs-bibtex", level="WARNING") as logs:
                plugin.format_citations([r"\cite{missing}"])
                plugin.format_citations([r"\cite[p. 2]{missing}"])

            first_build_warnings = [
                line for line in logs.output if "Citation key 'missing' not found" in line
            ]
            self.assertEqual(len(first_build_warnings), 1)

            plugin.on_config(config)
            with self.assertLogs("mkdocs.plugins.mkdocs-bibtex", level="WARNING") as logs2:
                plugin.format_citations([r"\cite{missing}"])

            second_build_warnings = [
                line for line in logs2.output if "Citation key 'missing' not found" in line
            ]
            self.assertEqual(len(second_build_warnings), 1)

    def test_formats_multi_key_latex_cite_blocks(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            quads = plugin.format_citations([r"\cite{smith2020,doe2021}"])
            self.assertEqual(len(quads), 2)
            self.assertEqual([q[1] for q in quads], ["smith2020", "doe2021"])
            self.assertEqual([q[2] for q in quads], ["mkbib-1", "mkbib-2"])

    def test_on_page_markdown_replaces_latex_cites_and_note(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = (
                r"First cite \cite[Section 4]{smith2020}. "
                r"Then multi \cite{smith2020,doe2021}."
            )
            rendered = self._render_html(plugin, markdown, config)

            self.assertNotIn(r"\cite", rendered)
            self.assertIn('id="fnref:mkbib-1"', rendered)
            self.assertIn('id="fnref:mkbib-2"', rendered)
            self.assertIn('<sup class="mkdocs-bibtex-citation-note">Section 4</sup>', rendered)
            self.assertIn('id="fn:mkbib-1"', rendered)
            self.assertIn('id="fn:mkbib-2"', rendered)

    def test_on_page_markdown_compacts_sorted_ranges(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = (
                r"\cite{smith2020}. "
                r"\cite{doe2021}. "
                r"\cite{lee2022}. "
                r"\cite{kim2023}. "
                r"\cite{patel2024}. "
                r"Range \cite{lee2022,patel2024,smith2020,doe2021}."
            )
            rendered = self._render_html(plugin, markdown, config)

            self.assertIn('id="fnref2:mkbib-1"', rendered)
            self.assertIn('id="fnref2:mkbib-2"', rendered)
            self.assertIn('id="fnref2:mkbib-3"', rendered)
            self.assertIn('id="fnref2:mkbib-5"', rendered)

    def test_on_page_markdown_puts_note_after_citation_refs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = r"\cite{smith2020}. \cite{doe2021}. Then \cite[Section 2]{smith2020,doe2021}."
            rendered = self._render_html(plugin, markdown, config)

            self.assertIn('id="fnref2:mkbib-1"', rendered)
            self.assertIn('id="fnref2:mkbib-2"', rendered)
            self.assertIn('<sup class="mkdocs-bibtex-citation-note">Section 2</sup>', rendered)

    def test_existing_markdown_footnotes_do_not_shift_citation_keys(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = (
                "Before footnote [^a].\n\n"
                "[^a]: Local footnote.\n\n"
                r"Then cite \cite{smith2020}.\n\n"
                r"Then cite range \cite{smith2020,doe2021}."
            )
            rendered = self._render_html(plugin, markdown, config)

            self.assertIn('id="fnref:a"', rendered)
            self.assertIn('id="fnref:mkbib-1"', rendered)
            self.assertIn('id="fnref2:mkbib-1"', rendered)
            self.assertIn('id="fnref:mkbib-2"', rendered)
            self.assertIn('id="fn:mkbib-1"', rendered)
            self.assertIn('id="fn:mkbib-2"', rendered)

    def test_repeated_identical_cite_blocks_are_all_replaced(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = r"One \cite{smith2020}. Two \cite{smith2020}."
            rendered = self._render_html(plugin, markdown, config)

            self.assertNotIn(r"\cite{smith2020}", rendered)
            self.assertIn('id="fnref:mkbib-1"', rendered)
            self.assertIn('id="fnref2:mkbib-1"', rendered)

    def test_legacy_pandoc_syntax_is_not_processed(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_dir = root / "bibliography"
            bib_dir.mkdir()
            bib_file = bib_dir / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_dir))
            plugin.config["bib_by_default"] = False
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            markdown = "Legacy [@smith2020] cite"
            rendered = plugin.on_page_markdown(markdown, page=None, config=config, files=None)
            self.assertEqual(rendered, markdown)


if __name__ == "__main__":
    unittest.main()
