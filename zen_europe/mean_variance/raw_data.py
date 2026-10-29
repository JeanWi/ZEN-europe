"""Read the raw data in ``data/raw_data/05-mean_variance``.

Files (see the README.md in that folder):

- ``Technology_classification.csv``: one row per technology with its IEA technology name, own TRL
  assessment, technology class. Exported from
  ``SD calculation.xlsx`` (sheet ``SDs``) and saved as UTF-8.
- ``TRL_IEA_technology_classification.csv``: technology readiness levels of
  the IEA ETP Clean Energy Technology Guide.
- ``TRL_SD_translation.csv``: relative standard deviation per TRL, following
  the AACE cost estimate classification.
- ``Technology_categories.csv``: allowed technology classes.
- ``relative_sd_import_price.csv`` and ``correlation_import_price.csv``:
  relative standard deviations and correlations of carrier import prices.
"""

from pathlib import Path

import pandas as pd


def read_technology_table(raw_folder: Path) -> pd.DataFrame:
    """Read Technology_classification.csv, indexed by technology, with the columns renamed for the code.

    Rows without a technology name (empty lines at the end of the Excel export)
    are dropped.
    """
    table = pd.read_csv(raw_folder / "Technology_classification.csv", encoding="utf-8")
    table.columns = table.columns.str.strip()
    table = table.rename(columns={table.columns[0]: "technology"})
    table = table.dropna(subset=["technology"]).set_index("technology")
    return table

def read_iea_trl(raw_folder: Path) -> pd.Series:
    """Read the TRL of 2024 per IEA technology name (names in lower case).

    Lower case, because Excel's XLOOKUP in ``SD calculation.xlsx`` ignores the
    case of the names.
    """
    table = pd.read_csv(raw_folder / "TRL_IEA_technology_classification.csv")
    trl = table.set_index(table["name"].str.lower())["trl2024"]
    return trl[~trl.index.duplicated(keep="first")]

def read_trl_to_relative_sd(raw_folder: Path) -> pd.Series:
    """Read the relative standard deviation per TRL (e.g. TRL 9 -> 0.1).

    The first line of the file holds the source, the values are percentages.
    """
    table = pd.read_csv(raw_folder / "TRL_SD_translation.csv", skiprows=1)
    table = table.dropna(subset=["TRL"])
    relative_sd = table["SD"].str.rstrip("%").astype(float) / 100
    return pd.Series(relative_sd.values, index=table["TRL"].astype(int), name="SD")

def read_import_price_relative_sd(raw_folder: Path) -> pd.Series:
    """Read the relative standard deviation of the import price per carrier."""
    table = pd.read_csv(raw_folder / "relative_sd_import_price.csv")
    return table.set_index("carrier")["relative_sd"]


def read_import_price_correlation(raw_folder: Path) -> pd.DataFrame:
    """Read the correlation matrix of the import prices (carrier x carrier)."""
    return pd.read_csv(raw_folder / "correlation_import_price.csv", index_col=0)


def raise_if_missing(required: list[str], available: pd.Index, path: Path) -> None:
    """Raise a readable error if elements of the model are missing in a raw file."""
    missing = [element for element in required if element not in available]
    if missing:
        raise ValueError(f"{path} has no entry for the model elements {missing}.")
