# Changelog

All notable changes to this project are documented in this file.

## Unreleased

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
