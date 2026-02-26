import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mkdocs_bibtex.plugin import BibTeXPlugin


class DummyConfig(dict):
    def __init__(self, config_file_path: str):
        super().__init__(config_file_path=config_file_path)
        self.config_file_path = config_file_path


class TestPluginBehavior(unittest.TestCase):
    def _write_sample_bib(self, path: Path):
        path.write_text(
            """@article{smith2020,
  title={Example Title},
  author={Smith, John},
  journal={Example Journal},
  year={2020}
}
""",
            encoding="utf-8",
        )

    def _make_plugin(self, bib_file: str) -> BibTeXPlugin:
        plugin = BibTeXPlugin()
        plugin.config = {
            "bib_file": bib_file,
            "footnote_format": "{number}",
            "bib_by_default": True,
            "bib_command": "\\bibliography",
            "full_bib_command": "\\full_bibliography",
        }
        return plugin

    def test_resolves_relative_bib_file_from_mkdocs_config_dir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            docs_dir = root / "docs"
            docs_dir.mkdir()
            mkdocs_file = docs_dir / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_file = root / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin("../refs.bib")
            config = DummyConfig(str(mkdocs_file))

            old_cwd = os.getcwd()
            try:
                os.chdir("/")
                plugin.on_config(config)
            finally:
                os.chdir(old_cwd)

            self.assertIn("smith2020", plugin.bib_data.entries)

    def test_rejects_url_bib_file_sources(self):
        plugin = self._make_plugin("https://example.com/refs.bib")
        config = DummyConfig("/tmp/mkdocs.yml")

        with self.assertRaises(Exception) as exc_info:
            plugin.on_config(config)

        self.assertIn("local path", str(exc_info.exception))

    def test_warns_unknown_key_once_per_build(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            mkdocs_file = root / "mkdocs.yml"
            mkdocs_file.write_text("site_name: Test\n", encoding="utf-8")

            bib_file = root / "refs.bib"
            self._write_sample_bib(bib_file)

            plugin = self._make_plugin(str(bib_file))
            config = DummyConfig(str(mkdocs_file))
            plugin.on_config(config)

            with self.assertLogs("mkdocs.plugins.mkdocs-bibtex", level="WARNING") as logs:
                plugin.format_citations(["[@missing]"])
                plugin.format_citations(["[@missing, p. 2]"])

            first_build_warnings = [
                line for line in logs.output if "Citation key 'missing' not found" in line
            ]
            self.assertEqual(len(first_build_warnings), 1)

            plugin.on_config(config)
            with self.assertLogs("mkdocs.plugins.mkdocs-bibtex", level="WARNING") as logs2:
                plugin.format_citations(["[@missing]"])

            second_build_warnings = [
                line for line in logs2.output if "Citation key 'missing' not found" in line
            ]
            self.assertEqual(len(second_build_warnings), 1)


if __name__ == "__main__":
    unittest.main()
