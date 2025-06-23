import re
import time
import validators
from collections import OrderedDict
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
from pybtex.database import BibliographyData, parse_file

from mkdocs_bibtex.utils import (
    find_cite_blocks,
    extract_cite_keys,
    format_bibliography,
    format_simple,
    insert_citation_keys,
    tempfile_from_url,
    log,
)


class BibTeXPlugin(BasePlugin):
    """
    MkDocs plugin for integrating BibTeX bibliography management into Markdown content.

    This plugin allows you to cite references using BibTeX keys in your Markdown files
    and automatically generates formatted bibliographies. It supports both local and
    remote BibTeX files, automatic bibliography insertion, and customizable citation
    formatting.

    Configuration Options:
        bib_file (str, optional): Path to a single BibTeX file or URL to a remote BibTeX file.
            Example URL: https://api.zotero.org/*/items?format=bibtex
        bib_dir (str, optional): Path to a directory containing BibTeX files. All .bib files
            in the directory will be recursively processed.
        bib_command (str): Command string to insert a page-specific bibliography.
            Defaults to "\\bibliography".
        bib_by_default (bool): Whether to automatically append the bibliography command
            to all pages. Defaults to True.
        full_bib_command (str): Command string to insert a complete bibliography of all
            references. Defaults to "\\full_bibliography".
        footnote_format (str): Format string for citation footnotes. Must include
            "{number}" placeholder. Defaults to "{number}".

    Note:
        Either bib_file or bib_dir must be specified, but not both.
    """

    config_scheme = [
        ("bib_file", config_options.Type(str, required=False)),
        ("bib_dir", config_options.Dir(exists=True, required=False)),
        ("bib_command", config_options.Type(str, default="\\bibliography")),
        ("bib_by_default", config_options.Type(bool, default=True)),
        ("full_bib_command", config_options.Type(str, default="\\full_bibliography")),
        ("footnote_format", config_options.Type(str, default="{number}")),
    ]

    def __init__(self):
        self.bib_data = None
        self.all_references = OrderedDict()
        self.unescape_for_arithmatex = False
        self.configured = False

    def on_startup(self, *, command, dirty):
        """
        Handle MkDocs startup event.

        This method tells MkDocs to keep the plugin object instance across rebuilds,
        which improves performance by avoiding re-initialization.

        Args:
            command: The MkDocs command being executed.
            dirty: Whether this is a dirty rebuild.
        """
        pass

    def on_config(self, config):
        """
        Load and parse bibliography data when configuration is loaded.

        This method is called when MkDocs loads the configuration. It loads BibTeX files
        from the specified source (file or directory), parses them, and caches the
        bibliography data for use during page processing. It also handles configuration
        validation and optimization for rebuilds.

        Args:
            config: The MkDocs configuration object.

        Returns:
            The configuration object (possibly modified).

        Raises:
            Exception: If neither bib_file nor bib_dir is specified, or if the
                footnote_format doesn't contain the required "{number}" placeholder.
        """

        bibfiles = []

        # Set bib_file from either url or path
        if self.config.get("bib_file", None) is not None:
            is_url = validators.url(self.config["bib_file"])
            # if bib_file is a valid URL, cache it with tempfile
            if is_url:
                bibfiles.append(
                    tempfile_from_url("bib file", self.config["bib_file"], ".bib")
                )
            else:
                bibfiles.append(self.config["bib_file"])
        elif self.config.get("bib_dir", None) is not None:
            bibfiles.extend(Path(self.config["bib_dir"]).rglob("*.bib"))
        else:  # pragma: no cover
            raise Exception("Must supply a bibtex file or directory for bibtex files")

        # load bibliography data
        refs = {}
        # log.info(f"BibTeXPlugin: loading data from bib files: {bibfiles}")
        for bibfile in bibfiles:
            log.debug(f"Parsing bibtex file {bibfile}")
            bibdata = parse_file(bibfile)
            refs.update(bibdata.entries)

        if hasattr(self, "last_configured"):
            # Skip rebuilding bib data if all files are older than the initial config
            if all(
                Path(bibfile).stat().st_mtime < self.last_configured
                for bibfile in bibfiles
            ):
                # log.info("BibTeXPlugin: no changes in bibfiles")
                return config

        # Clear references on reconfig
        self.all_references = OrderedDict()

        self.bib_data = BibliographyData(entries=refs)

        if "{number}" not in self.config.get("footnote_format"):
            raise Exception("Must include `{number}` placeholder in footnote_format")

        self.footnote_format = self.config.get("footnote_format")

        self.last_configured = time.time()
        return config

    def on_page_markdown(self, markdown, page, config, files):
        """
        Process markdown content to handle citations and bibliography generation.

        This method processes each page's markdown content to:
        1. Find and extract citation keys from the text
        2. Convert citation keys to properly formatted footnote references
        3. Insert formatted citations back into the text
        4. Generate and insert page-specific bibliographies
        5. Generate and insert full bibliographies when requested

        Args:
            markdown (str): The raw markdown content of the page.
            page: The MkDocs page object being processed.
            config: The MkDocs configuration object.
            files: The collection of all files in the documentation.

        Returns:
            str: The processed markdown content with citations and bibliographies inserted.
        """

        # 1. Grab all the cited keys in the markdown
        cite_keys = find_cite_blocks(markdown)

        # 2. Convert all the citations to text references
        citation_quads = self.format_citations(cite_keys)

        # 3. Convert cited keys to footnote references
        markdown = insert_citation_keys(citation_quads, markdown)

        # 4. Insert in the bibliography text into the markdown
        bib_command = self.config.get("bib_command", "\\bibliography")

        if self.config.get("bib_by_default"):
            markdown += f"\n{bib_command}"

        bibliography = format_bibliography(citation_quads)
        markdown = re.sub(
            re.escape(bib_command),
            bibliography,
            markdown,
        )

        # 5. Build the full Bibliography and insert into the text
        full_bib_command = self.config.get("full_bib_command", "\\full_bibliography")

        markdown = re.sub(
            re.escape(full_bib_command),
            self.full_bibliography,
            markdown,
        )

        return markdown

    def format_footnote_key(self, number):
        """
        Generate a formatted footnote key based on the configured format.

        Args:
            number (int): The citation number to format.

        Returns:
            str: The formatted footnote key according to the footnote_format configuration.
        """
        return self.footnote_format.format(number=number)

    def format_citations(self, cite_keys):
        """
        Convert citation keys to formatted citation quads and register them globally.

        This method processes a list of citation keys, formats them according to the
        bibliography style, assigns numbers, and creates citation quads containing
        all necessary information for rendering. It also maintains a global registry
        of all references used across the documentation.

        Args:
            cite_keys (list): List of citation key strings, which may be compound
                (containing multiple keys separated by semicolons).

        Returns:
            list: List of citation quads, where each quad is a tuple containing:
                - Full citation block (str): The original citation text
                - Individual key (str): A single citation key
                - Formatted footnote (str): The formatted footnote reference
                - Citation text (str): The formatted bibliography entry
        """

        # Deal with arithmatex fix at some point

        # 1. Extract the keys from the keyset
        entries = OrderedDict()
        pairs = [
            [cite_block, key]
            for cite_block in cite_keys
            for key in extract_cite_keys(cite_block)
        ]
        keys = list(OrderedDict.fromkeys([k for _, k in pairs]).keys())
        numbers = {k: str(n + 1) for n, k in enumerate(keys)}

        # Remove non-existant keys from pairs
        pairs = [p for p in pairs if p[1] in self.bib_data.entries]

        # 2. Collect any unformatted reference keys
        for _, key in pairs:
            if key not in self.all_references:
                entries[key] = self.bib_data.entries[key]

        # 3. Format entries using simple formatting
        log.debug("Formatting all bib entries...")
        self.all_references.update(format_simple(entries))
        log.debug("SUCCESS Formatting all bib entries")

        # 4. Construct quads
        quads = [
            (
                cite_block,
                key,
                self.format_footnote_key(numbers[key]),
                self.all_references[key],
            )
            for cite_block, key in pairs
        ]

        # List the quads in order to remove duplicate entries
        return list(dict.fromkeys(quads))

    @property
    def full_bibliography(self):
        """
        Generate the complete bibliography containing all references used in the documentation.

        Returns:
            str: A formatted string containing all bibliography entries as footnotes,
                numbered sequentially in the order they were first encountered.
        """

        bibliography = []
        for number, (key, citation) in enumerate(self.all_references.items()):
            bibliography_text = "[^{}]: {}".format(
                number,
                citation,
            )
            bibliography.append(bibliography_text)

        return "\n".join(bibliography)
