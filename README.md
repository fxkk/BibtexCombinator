# Bibfile Consolidation Pipeline

A Python script to consolidate BibTeX files from multiple scientific databases into a single Excel spreadsheet with deduplication and standardized formatting.

## Overview

This project processes BibTeX (`.bib`) files exported from various scientific databases (Web of Science, Scopus, ScienceDirect, etc.) and consolidates them into a unified Excel spreadsheet with standardized formatting and duplicate detection.

## Features

- **Multi-source consolidation**: Combines BibTeX files from different academic databases
- **Automatic duplicate detection**: Identifies and separates duplicate entries based on DOI
- **Data normalization**: Standardizes journal names, DOI formats, and field names
- **Journal alias mapping**: Unifies different representations of the same journal
- **Excel output**: Generates a spreadsheet with separate sheets for unique entries and duplicates
- **Source tracking**: Each entry retains information about its origin database

## Installation

This project uses `uv` for dependency management. Install dependencies with:

```bash
uv sync
```

## Usage

### Place BibTeX files in the `sources/` directory

Export your search results from academic databases in BibTeX format and save them to the `sources/` folder:

```
sources/
├── scopus.bib
├── web_of_science.bib
└── sciencedirect.bib
```

### Run the script

```bash
uv run main.py
```

### Review the output

The script generates `bibfile_summary.xlsx` with two sheets:

- **Unique Entries**: Deduplicated references (first occurrence kept)
- **Duplicates**: Duplicate entries with information about which source contains the original

## Output Format

### Columns included in the output:

- `doi`: Digital Object Identifier (normalized, prefix removed)
- `title`: Article title
- `journal`: Journal name (title case, aliases unified)
- `year`: Publication year
- `author`: Author list
- `url`: Article URL
- `keywords`: Keywords/tags
- `entry_type`: Type of publication (article, conference paper, etc.)
- `source`: Origin database (derived from filename)
- `abstract`: Article abstract

## Configuration

Edit the `Config` class in `main.py` to customize:

### Relevant Columns

Define which fields to include in the output:

```python
relevant_columns = [
    'doi', 'title', 'journal', 'year', 'author',
    'url', 'keywords', 'entry_type', 'source', 'abstract'
]
```

### Journal Aliases

Map different journal name variations to a standard name:

```python
journal_aliases = {
    "Energy Research & Social Science": [
        "Energy Research And Social Science",
        "Energy Research \\& Social Science"
    ]
}
```