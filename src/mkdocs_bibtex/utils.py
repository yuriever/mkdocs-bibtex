import logging
import re
from collections import OrderedDict
from itertools import groupby

from pybtex.backends.markdown import Backend as MarkdownBackend
from pybtex.style.formatting.plain import Style as PlainStyle

# Grab a logger
log = logging.getLogger("mkdocs.plugins.mkdocs-bibtex")

# Matches \cite{author}, \cite[Section 2]{author}, and \cite{author1,author2}
# Group 1: optional note in square brackets (without brackets)
# Group 2: one-or-more keys in braces (comma-separated, without braces)
CITE_BLOCK_RE = re.compile(r"\\cite\b(?:\s*\[([^\[\]]*?)\])?\s*\{([^{}]+)\}")


def _extract_suffix_from_cite_block(cite_block):
    """Extract optional note from a cite block."""
    match = CITE_BLOCK_RE.fullmatch(cite_block.strip())
    if not match or not match.group(1) or not match.group(1).strip():
        return ""
    return match.group(1).strip()


def _render_bibliography_entries(entries):
    """Render bibliography entries as markdown footnotes for unified numbering."""
    bibliography = []
    for key, citation in entries.items():
        bibliography_text = "[^{}]: {}".format(key, citation)
        bibliography.append(bibliography_text)

    return "\n".join(bibliography)


def format_simple(entries):
    """
    Format bibliography entries using pybtex's plain style.

    Args:
        entries (dict): Dictionary of bibliography entries to format.

    Returns:
        dict: Dictionary mapping entry keys to formatted citation text.
    """
    style = PlainStyle()
    backend = MarkdownBackend()
    citations = OrderedDict()
    for key, entry in entries.items():
        log.debug(f"Formatting bibtex entry {key!r}")
        formatted_entry = style.format_entry("", entry)
        entry_text = formatted_entry.text.render(backend)
        entry_text = entry_text.replace("\n", " ")
        # Local reference list for this file
        citations[key] = (
            entry_text.replace("\\(", "(").replace("\\)", ")").replace("\\.", ".")
        )
        log.debug(f"SUCCESS Formatting bibtex entry {key!r}")
    return citations


def extract_cite_keys(cite_block):
    """
    Extract citation keys from a citation block.

    Args:
        cite_block (str): Citation block containing one or more citation keys.

    Returns:
        list: List of citation keys found in the block.
    """
    match = CITE_BLOCK_RE.fullmatch(cite_block.strip())
    if not match:
        return []

    keys_group = match.group(2)
    return [tok.strip() for tok in keys_group.split(",") if tok.strip()]


def find_cite_blocks(markdown):
    """
    Find citation blocks in markdown text.

    Args:
        markdown (str): The markdown text to search for citation blocks.

    Returns:
        list: List of citation block strings found in the markdown.

    Examples:
        Matches: \\cite{author}, \\cite[Section 2]{author}, \\cite{author1,author2}
        Does NOT match: \\parencite{author}, [@author]
    """
    citation_blocks = [matches.group(0) for matches in CITE_BLOCK_RE.finditer(markdown)]

    return citation_blocks


def insert_citation_keys(citation_quads, markdown):
    """
    Replace citation blocks with generated citation keys in markdown text.

    Args:
        citation_quads (tuple): Tuple containing citation information.
        markdown (str): The markdown text to modify.

    Returns:
        str: Modified markdown with native footnote refs replacing cite blocks.
    """

    log.debug("Replacing citation keys with the generated ones...")

    # Renumber quads if using numbers for citation links

    grouped_quads = [list(g) for _, g in groupby(citation_quads, key=lambda x: x[0])]
    for quad_group in grouped_quads:
        full_citation = quad_group[0][0][1]  # the full citation block
        cite_keys = [quad[2] for quad in quad_group]
        footnote_refs = "".join(["[^{}]".format(key) for key in cite_keys])

        suffix = _extract_suffix_from_cite_block(full_citation)
        replacement_citation = footnote_refs
        if suffix:
            replacement_citation = "{} <sup class=\"mkdocs-bibtex-citation-note\">{}</sup>".format(
                replacement_citation,
                suffix,
            )

        markdown = markdown.replace(full_citation, replacement_citation, 1)

    log.debug("SUCCESS Replacing citation keys with the generated ones")

    return markdown


def format_bibliography(citation_quads):
    """
    Generate a bibliography from citation information.

    Args:
        citation_quads (tuple): Tuple containing citation information.

    Returns:
        str: Markdown-formatted bibliography as a string.
    """
    new_bib = {quad[2]: quad[3] for quad in citation_quads}
    return _render_bibliography_entries(new_bib)
