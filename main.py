from pathlib import Path
import pandas as pd
import bibtexparser
from typing import List, Dict, Any

class Config:
    sources_dir: str = "sources"
    relevant_columns = [
        'doi',
        'title',
        'journal',
        'year',
        'author',
        'url',
        'keywords',
        'entry_type',
        'source',
        'abstract'
    ]

    journal_aliases = {
        "Energy Research & Social Science": ["Energy Research And Social Science", "Energy Research \\& Social Science"]
    }

    
def filter_for_duplicates(df: pd.DataFrame):
    # Remove duplicates based on 'doi' column, keeping the first occurrence
    unique_df = df.drop_duplicates(subset=['doi'], keep='first')

    # Find duplicates (all except the first occurrence)
    duplicates_df = df[df.duplicated(subset=['doi'], keep='first')].copy()

    # Map DOI to source of the kept entry
    doi_to_source = unique_df.set_index('doi')['source'].to_dict()
    duplicates_df['duplicate_in'] = duplicates_df['doi'].map(doi_to_source)

    return unique_df, duplicates_df


def apply_column_transformations(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    # Unify DOI format: remove 'https://doi.org/' prefix if present
    if 'doi' in df.columns:
        df['doi'] = df['doi'].str.replace(r'^https?://doi\.org/', '', regex=True)

    # journal names can be in different cases, unify to title case
    if 'journal' in df.columns:
        df['journal'] = df['journal'].str.title()

    # Apply journal aliases
    if 'journal' in df.columns:
        for standard_name, aliases in config.journal_aliases.items():
            df['journal'] = df['journal'].replace(aliases, standard_name)

    return df

def reduce_df_to_relevant_columns(df: pd.DataFrame, config: Config) -> pd.DataFrame:
    
    reduced_df = df[config.relevant_columns].copy()
    
    return reduced_df


def read_bib_file(file_path: str, source_tag: str) -> List[Dict[str, Any]]:
    """Returns a list of entries like:
    [
        {
            'entry_type': 'spellbook',
            'entry_key': 'ELDRYN2025123456',
            'title': 'The Dragonfire Conundrum: Harnessing Arcane Flames for Magical Energy',
            'journal': 'Journal of Arcane Engineering',
            'volume': '42',
            'pages': '123456',
            'year': '2025',
            'issn': '1234-5678',
            'doi': 'https://doi.org/10.1234/jae.2025.123456',
            'url': 'https://www.arcanejournals.com/spellbook/ELDRYN2025123456',
            'author': 'Eldryn Starweaver and Mira Shadowdancer and Thalion Silverleaf',
            'keywords': 'Dragonfire, Arcane energy, Spellcasting, Magical safety, Enchantment, Mana storage',
            'abstract': 'In the age of high fantasy, dragonfire has emerged as a potent source of magical energy, capable of powering spells and enchanted artifacts across the realms. This review explores the challenges of safely storing and utilizing dragonfire, examining its thermomagical properties and the risks associated with uncontrolled arcane reactions. The study presents a framework for integrating dragonfire into existing mana grids, discusses the environmental impact of magical emissions, and highlights the importance of wizard guild regulations for public safety. The findings suggest that a sustainable magical economy requires innovative spellcraft, robust containment wards, and cross-realm collaboration among mages and magical creatures.'
        }
    ]
    """

    bib_database = bibtexparser.parse_file(file_path)

    entries = []
    for entry in bib_database.entries:
        entry_dict = {
            'entry_type': entry.entry_type,
            'entry_key': entry.key,
            'source': source_tag,
        }
        for field in entry.fields:
            # override source from bib file with filename-based source_tag
            if field.key.lower() != "source":
                entry_dict[field.key.lower()] = field.value
        
        entries.append(entry_dict)
    
    return entries


def combine_bib_files_to_df(sources_dir: str) -> pd.DataFrame:

    sources_path = Path(sources_dir)
    
    if not sources_path.exists():
        raise FileNotFoundError(f"Sources directory '{sources_dir}' not found")
    
    # Find all .bib files
    bib_files = list(sources_path.glob('*.bib'))
    
    if not bib_files:
        raise FileNotFoundError(f"No .bib files found in '{sources_dir}'")
    
    all_entries = []
    
    for bib_file in bib_files:
        try:
            entries = read_bib_file(bib_file.absolute(), source_tag=str(bib_file.stem).lower())

            all_entries.extend(entries)
                
        except Exception as e:
            print(f"  Error processing {bib_file.name}: {e}")
            continue

    df = pd.DataFrame(all_entries)

    return df


def main():

    config = Config()
    
    # Consolidate all .bib files
    df = combine_bib_files_to_df(config.sources_dir)

    df = apply_column_transformations(df, config)

    df = reduce_df_to_relevant_columns(df, config)

    unique_entries_df, duplicates_df = filter_for_duplicates(df)

    with pd.ExcelWriter('bibfile_summary.xlsx', engine='openpyxl') as writer:
        unique_entries_df.to_excel(writer, sheet_name='Unique Entries', index=False)
        duplicates_df.to_excel(writer, sheet_name='Duplicates', index=False)


if __name__ == "__main__":
    df = main()
