# Changelog

All notable changes to this project are documented in this file.

## Unreleased

## 2.3.3 - 2026-03-17

### Fixed

- Restored native Markdown footnote semantics for citation refs.
    - Citation refs are now emitted as markdown footnote references and are no longer rebuilt
        through HTML regex rewriting.
    - `fnref` ids and bibliography backrefs are now produced by the Markdown footnotes engine,
        preserving standard linking behavior.
- Fixed duplicate cite-block replacement stability while keeping per-occurrence replacement.

### Changed

- Optional cite notes are rendered after citation refs using
    `<sup class="mkdocs-bibtex-citation-note">...` for consistent superscript styling.

## 2.3.2 - 2026-03-17

### Changed

- Compact citation punctuation is now CSS-driven rather than hardcoded text.
    - Citation output no longer injects literal `[` and `]` characters.
    - Citations render as structured spans (`mkdocs-bibtex-citation`,
        `mkdocs-bibtex-citation-body`, `mkdocs-bibtex-citation-note`) so bracket and comma
        formatting can be customized with `::before` and `::after`.
- Citation link styling now uses the dedicated class `mkdocs-bibtex-cite-ref` without
    inheriting default superscript styling from theme footnote classes.

## 2.3.1 - 2026-03-17

### Fixed

- Merged citation references with existing Markdown footnotes so numbering is coherent in one
    shared footnote sequence.
    - Example: if `[^a]` appears before `\cite{key}`, the citation label follows after that
        footnote number.
- Preserved compact LaTeX-style citation rendering (`[n]`, `[n-m]`, `[n-m, note]`) while using
    the shared Markdown footnote numbering.
    - Range endpoints remain clickable and point to the correct footnote entries.

## 2.3.0 - 2026-03-17

### Changed

- Inline `\cite` output now uses a single compact bracket format with ordered numbers and range compaction.
    - Example: `[1][2]` style output became `[1-2]`.
    - Mixed sequences are rendered like `[1-3,5]`.
- Optional cite notes are now rendered inside the same citation bracket.
    - Example: `\cite[Section 2]{a,b}` now renders as `[1-2, Section 2]`.

### Fixed

- Fixed numbering conflicts when pages already contain Markdown footnotes (`[^a]`, `[^b]`, etc.).
    - Follow-up in `2.3.1` merged numbering into one coherent sequence.

## 2.1.0 - 2026-03-01

### Breaking Changes

- Replaced Pandoc-style inline citation parsing (e.g. `[@author]`) with LaTeX-style `\cite` parsing.
- Legacy `[@...]` citations are no longer recognized.
- Removed `bib_file` configuration support; `bib_dir` is now the only bibliography source option.

### Added

- Added support for `\cite{key}`, `\cite[note]{key}`, and comma-separated key lists in `\cite{key1,key2}`.
- Citation key parsing now splits on commas, trims surrounding whitespace per key, and allows internal spaces in keys.

### Dependencies

- Constrained MkDocs to `>=1.6,<2.0` to avoid the breaking MkDocs 2.x line.

## 2.0.1 - 2026-02-27

- Added

    - Added support for semicolon-separated inline citation blocks (e.g. [@author; @doe]).
        - `CITE_BLOCK_RE` now recognizes multiple `@key` tokens separated by `;`.
        - `extract_cite_keys` returns multiple citation keys for a single citation block.

## 2.0.0 - 2026-02-26

### Breaking Changes

- Removed all remote bibliography source support; `bib_file` now accepts local file paths only.
- Removed Zotero-specific download/pagination handling.
- URL values for `bib_file` now raise a configuration error.

### Changed

- Relative `bib_file` paths now resolve from the directory containing `mkdocs.yml`.
- Missing citation keys are now logged once per unique key per build.

### Dependencies

- Removed runtime dependencies on `requests` and `validators`.
