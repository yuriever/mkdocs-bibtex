# MkDocs BibTeX Plugin

A [MkDocs](https://www.mkdocs.org/) plugin for citation management using BibTeX files.

## Installation

Install the plugin using pip:

``` bash
pip install mkdocs-bibtex
```

## Quick Start

1. Add the plugin to your `mkdocs.yml` configuration:

    ``` yaml
    plugins:
    - search
    - bibtex:
        bib_file: "refs.bib"

    markdown_extensions:
    - footnotes
    ```

2. Create a BibTeX file (e.g., `refs.bib`) in your project root
3. Use citations in your markdown files
4. The bibliography will be automatically generated

> **Note:** The `footnotes` extension is required for citation linking functionality.

## Configuration Options

| Option             | Type      | Default              | Description                                                                                     |
| ------------------ | --------- | -------------------- | ----------------------------------------------------------------------------------------------- |
| `bib_file`         | `string`  | -                    | Path to a single local BibTeX file. Can be absolute or relative to `mkdocs.yml`                 |
| `bib_dir`          | `string`  | -                    | Directory containing BibTeX files to load (alternative to `bib_file`)                           |
| `bib_command`      | `string`  | `\bibliography`      | Command syntax to render bibliography in markdown                                               |
| `bib_by_default`   | `boolean` | `true`               | Automatically append bibliography to every markdown document                                    |
| `full_bib_command` | `string`  | `\full_bibliography` | Command syntax to render complete bibliography                                                  |

### Example Configurations

**Local BibTeX file:**

```yaml
plugins:
  - bibtex:
      bib_file: "references/my_refs.bib"
```

**Multiple BibTeX files:**

```yaml
plugins:
  - bibtex:
      bib_dir: "bibliography/"
```

**Custom commands:**

```yaml
plugins:
  - bibtex:
      bib_file: "refs.bib"
      bib_command: "\\references"
      full_bib_command: "\\complete_bibliography"
      bib_by_default: false
```

## Usage

### Basic Citations

Use standard citation syntax in your markdown files. The plugin will automatically generate the bibliography based on your configuration.

### Manual Bibliography Placement

If you set `bib_by_default: false`, you can manually place the bibliography using:

```markdown
\bibliography
```

### Complete Bibliography

To render all entries from your BibTeX files:

```markdown
\full_bibliography
```

## Requirements

- MkDocs
- Python 3.7+
- `footnotes` markdown extension
