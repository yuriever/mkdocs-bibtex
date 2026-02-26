import logging
import re
from collections import OrderedDict
from itertools import groupby

from pybtex.backends.markdown import Backend as MarkdownBackend
from pybtex.style.formatting.plain import Style as PlainStyle

# Grab a logger
log = logging.getLogger("mkdocs.plugins.mkdocs-bibtex")

# Matches only [@author] and [@author, suffix]
# Group 1: @author (without brackets)
# Group 2: optional suffix (without brackets)
CITE_BLOCK_RE = re.compile(r"\[(@[^\s,\]]+)(?:,\s*([^\[\]]+?))?\]")


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
        log.debug(f"Converting bibtex entry {key!r} without pandoc")
        formatted_entry = style.format_entry("", entry)
        entry_text = formatted_entry.text.render(backend)
        entry_text = entry_text.replace("\n", " ")
        # Local reference list for this file
        citations[key] = (
            entry_text.replace("\\(", "(").replace("\\)", ")").replace("\\.", ".")
        )
        log.debug(f"SUCCESS Converting bibtex entry {key!r} without pandoc")
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

    return [match.group(1)[1:]]


def find_cite_blocks(markdown):
    """
    Find citation blocks in markdown text.

    Args:
        markdown (str): The markdown text to search for citation blocks.

    Returns:
        list: List of citation block strings found in the markdown.

    Examples:
        Matches: [@author], [@author, p. 123]
        Does NOT match: [mail@example.com], [@author; @doe], [-@author]

    Note:
        Uses regex pattern: \\[(@[^\\s,\\]]+)(?:,\\s*([^\\[\\]]+?))?\\]
        - Group 1: Citation key including @ symbol (without brackets)
        - Group 2: Optional suffix after comma (without brackets)
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
        str: Modified markdown with citation keys replaced.
    """

    log.debug("Replacing citation keys with the generated ones...")

    # Renumber quads if using numbers for citation links

    grouped_quads = [list(g) for _, g in groupby(citation_quads, key=lambda x: x[0])]
    for quad_group in grouped_quads:
        full_citation = quad_group[0][0]  # the full citation block
        replacement_citation = "".join(["[^{}]".format(quad[2]) for quad in quad_group])

        # Extract suffix from the citation block using the same regex as find_cite_blocks
        match = CITE_BLOCK_RE.fullmatch(full_citation.strip())
        suffix = ""
        if match and match.group(2) and match.group(2).strip():  # group 2 is the suffix
            suffix = " " + match.group(2).strip()

        # Add suffix to replacement citation
        replacement_citation = replacement_citation + suffix
        markdown = markdown.replace(full_citation, replacement_citation)

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
    bibliography = []
    for key, citation in new_bib.items():
        bibliography_text = "[^{}]: {}".format(key, citation)
        bibliography.append(bibliography_text)

    return "\n".join(bibliography)
