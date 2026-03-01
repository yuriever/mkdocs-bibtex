# MkDocs BibTeX Plugin

MkDocs plugin for BibTeX citations and bibliography rendering.

## Install

```bash
pip install mkdocs-bibtex
```

## Quick Start

Add this to `mkdocs.yml`:

```yaml
plugins:
  - bibtex:
      bib_dir: "bibliography/"

markdown_extensions:
  - footnotes
```

Then:

1. Put one or more `.bib` files in `bibliography/`.
2. Add citations in Markdown using `\cite{...}`.
3. Build your docs; bibliography entries are rendered automatically.

## Citation Syntax

```markdown
\cite{author1}
\cite[Section 1]{author1}
\cite{author1,other2}
```

## Bibliography Commands

- `\bibliography`: Render referenced entries.
- `\full_bibliography`: Render all loaded entries.

If you set `bib_by_default: false`, place `\bibliography` manually where you want it.

## Config

| Option | Default | Required | Description |
| --- | --- | --- | --- |
| `bib_dir` | - | Yes | Directory containing `.bib` files. |
| `bib_command` | `\bibliography` | No | Markdown command for referenced bibliography. |
| `full_bib_command` | `\full_bibliography` | No | Markdown command for full bibliography. |
| `bib_by_default` | `true` | No | Append bibliography automatically to each page. |
