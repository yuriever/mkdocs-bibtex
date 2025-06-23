import logging
import re
import requests
import tempfile
import urllib.parse
from collections import OrderedDict
from itertools import groupby
from pathlib import Path
from packaging.version import Version

import mkdocs

from pybtex.backends.markdown import Backend as MarkdownBackend
from pybtex.database import BibliographyData
from pybtex.style.formatting.plain import Style as PlainStyle

# Grab a logger
log = logging.getLogger("mkdocs.plugins.mkdocs-bibtex")


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
    cite_regex = re.compile(r"@([^\s,\]]+)")
    cite_keys = re.findall(cite_regex, cite_block)

    return cite_keys


def find_cite_blocks(markdown):
    """
    Find citation blocks in markdown text.

    Args:
        markdown (str): The markdown text to search for citation blocks.

    Returns:
        list: List of citation block strings found in the markdown.

    Examples:
        Matches: [@author], [@author, p. 123], [@author, my suffix here]
        Does NOT match: [mail@example.com], [@author; @doe]

    Note:
        Uses regex pattern: (\[(-{0,1}@\S+)(?:,\s*(.*?))?\])
        - Group 1: Entire citation block (returned value)
        - Group 2: Citation key including @ symbol
        - Group 3: Optional suffix after comma
    """
    r = r"(\[(-{0,1}@\S+)(?:,\s*(.*?))?\])"
    cite_regex = re.compile(r)

    citation_blocks = [
        # We only care about the block (group 1)
        (matches.group(1))
        for matches in re.finditer(cite_regex, markdown)
    ]

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
        cite_regex = re.compile(r"(\[(-{0,1}@\S+)(?:,\s*(.*?))?\])")
        match = cite_regex.search(full_citation)
        suffix = ""
        if match and match.group(3) and match.group(3).strip():  # group 3 is the suffix
            suffix = " " + match.group(3).strip()

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


def tempfile_from_url(name, url, suffix):
    """
    Download content from URL and save to a temporary file.

    Args:
        name (str): Name identifier for logging purposes.
        url (str): URL to download content from.
        suffix (str): File extension for the temporary file.

    Returns:
        str: Path to the created temporary file.

    Raises:
        RuntimeError: If download fails after 3 attempts or receives non-200 status.
    """
    log.debug(f"Downloading {name} from URL {url} to temporary file...")
    if urllib.parse.urlparse(url).hostname == "api.zotero.org":
        return tempfile_from_zotero_url(name, url, suffix)
    for i in range(3):
        try:
            dl = requests.get(url)
            if dl.status_code != 200:  # pragma: no cover
                raise RuntimeError(
                    f"Couldn't download the url: {url}.\n Status Code: {dl.status_code}"
                )

            file = tempfile.NamedTemporaryFile(
                mode="wt", encoding="utf-8", suffix=suffix, delete=False
            )
            file.write(dl.text)
            file.close()
            log.info(f"{name} downloaded from URL {url} to temporary file ({file})")
            return file.name

        except requests.exceptions.RequestException:  # pragma: no cover
            pass
    raise RuntimeError(
        f"Couldn't successfully download the url: {url}"
    )  # pragma: no cover


def tempfile_from_zotero_url(name: str, url: str, suffix: str) -> str:
    """
    Download bibliography data from Zotero API and save to temporary file.

    Handles pagination to download all available items from the Zotero API.

    Args:
        name: Name identifier for logging purposes.
        url: Zotero API URL to download from.
        suffix: File extension for the temporary file.

    Returns:
        Path to the created temporary file containing all downloaded data.

    Raises:
        RuntimeError: If download fails or receives non-200 status.
    """
    log.debug(f"Downloading {name} from Zotero at {url}")
    bib_contents = ""

    url = sanitize_zotero_query(url)

    # Limit the pages requested to 999 arbitrarily. This will support a maximum of ~100k items
    for page_num in range(999):
        for _ in range(3):
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    msg = f"Couldn't download the url: {url}.\nStatus Code: {response.status_code}"
                    raise RuntimeError(msg)
                break
            except requests.exceptions.RequestException:  # pragma: no cover
                pass

        bib_contents += response.text
        try:
            url = response.links["next"]["url"]
        except KeyError:
            log.debug(f"Downloaded {page_num}(s) from {url}")
            break
    else:
        log.debug(f"Exceeded the maximum number of pages. Found: {page_num} pages")
    with tempfile.NamedTemporaryFile(
        mode="wt", encoding="utf-8", suffix=suffix, delete=False
    ) as file:
        file.write(bib_contents)
    log.info(f"{name} downloaded from URL {url} to temporary file ({file})")
    return file.name


def sanitize_zotero_query(url: str) -> str:
    """
    Sanitize and update query parameters for Zotero API URLs.

    Ensures the URL requests data in bibtex format with maximum items per page
    to optimize download performance.

    Args:
        url: Original Zotero API URL.

    Returns:
        Updated URL with sanitized query parameters.
    """
    updated_query_params = {"format": "bibtex", "limit": 100}

    parsed_url = urllib.parse.urlparse(url)

    query_params = dict(urllib.parse.parse_qsl(parsed_url.query))

    return urllib.parse.ParseResult(
        scheme=parsed_url.scheme,
        netloc=parsed_url.netloc,
        path=parsed_url.path,
        params=parsed_url.params,
        query=urllib.parse.urlencode({**query_params, **updated_query_params}),
        fragment=parsed_url.fragment,
    ).geturl()
