# Changelog

All notable changes to this project are documented in this file.

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
