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

## Citation Output

Inline citations are rendered as native Markdown footnote references:

- Single citation: one footnote-style reference.
- Multiple citations: adjacent footnote-style references.
- Optional notes are rendered after citation refs in superscript note markup.

Citation numbers are coherent with existing Markdown footnotes in the same page.

If a page already contains footnotes (for example `[^a]`), citation numbers continue from that sequence.

By default, citation numbers in inline refs link to entries in the page footnote list.

Unknown citation keys are rendered as visible inline markers (instead of disappearing), so they
are easy to find in generated HTML.
Example: `\\cite{xxxx}` renders `[xxxx]` with class `mkdocs-bibtex-missing-citation`.

## Bibliography Commands

- `\bibliography`: Render referenced entries.
- `\full_bibliography`: Render all loaded entries.

If you set `bib_by_default: false`, place `\bibliography` manually where you want it.

## Bibliography Markup and Styling

Bibliography entries are rendered as Markdown footnotes, so they follow your theme's existing footnote styles automatically.

Citation labels are emitted as native footnote refs so MkDocs/Python-Markdown generates standard `fnref`/`fn` ids and backrefs.

Citation refs are rendered using footnote-style markup:

```html
<sup id="fnref:mkbib-1">
  <a class="footnote-ref" href="#fn:mkbib-1">2</a>
</sup>
```

Suggested CSS:

```css
.mkdocs-bibtex-citation-note {
  margin-left: 0.25em;
  font-size: inherit;
  vertical-align: super;
}

.mkdocs-bibtex-missing-citation {
  color: #b00020;
  font-weight: 600;
}
```

## Config

| Option | Default | Required | Description |
| --- | --- | --- | --- |
| `bib_dir` | - | Yes | Directory containing `.bib` files. |
| `bib_command` | `\bibliography` | No | Markdown command for referenced bibliography. |
| `full_bib_command` | `\full_bibliography` | No | Markdown command for full bibliography. |
| `bib_by_default` | `true` | No | Append bibliography automatically to each page. |
| `footnote_format` | `{number}` | No | Number format for citation labels (must include `{number}`). |
