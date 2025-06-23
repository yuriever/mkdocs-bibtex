[![testing](https://github.com/shyamd/mkdocs-bibtex/workflows/testing/badge.svg)](https://github.com/shyamd/mkdocs-bibtex/actions?query=workflow%3Atesting)
[![codecov](https://codecov.io/gh/shyamd/mkdocs-bibtex/branch/main/graph/badge.svg)](https://codecov.io/gh/shyamd/mkdocs-bibtex)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/shyamd/mkdocs-bibtex.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/shyamd/mkdocs-bibtex/context:python)


# mkdocs-bibtex

A [MkDocs](https://www.mkdocs.org/) plugin for citation management using bibtex.


## Setup

Install the plugin using pip:

```
pip install mkdocs-bibtex
```


Next, add the following lines to your `mkdocs.yml`:

```yml
plugins:
  - search
  - bibtex:
      bib_file: "refs.bib"
markdown_extensions:
  - footnotes
```

The footnotes extension is how citations are linked for now.

> If you have no `plugins` entry in your config file yet, you'll likely also want to add the `search` plugin. MkDocs enables it by default if there is no `plugins` entry set.


## Options

- `bib_file` - The path or url to a single bibtex file. Path can either be absolute or relative to `mkdocs.yml`. Example URL: `https://api.zotero.org/*/items?format=bibtex`
- `bib_dir` - Directory for bibtex files to load, same as above for path resolution
- `bib_command` - The syntax to render your bibliography, defaults to `\bibliography`
- `bib_by_default` - Automatically append the `bib_command` at the end of every markdown document, defaults to `true`
- `full_bib_command` - The syntax to render your entire bibliography, defaults to `\full_bibliography`

