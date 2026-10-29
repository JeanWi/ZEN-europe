"""Relative standard deviation of the technology capex and the import prices.

The relative standard deviation (relative sd) is the standard deviation of a
cost as a share of the cost itself, e.g. 0.1 = 10 %.

Import prices: hand-set values per carrier in ``relative_sd_import_price.csv``.

Technology capex: one method is available (setting
``mean_variance.technology_relative_sd_source``):

``trl`` (the calculation of ``SD calculation.xlsx``)
    1. The technology readiness level (TRL) is the ``trl2024`` of the IEA
       technology named in the column "Tec in IEA TRL classification".
       Technologies without IEA entry (e.g. "Incumbent") use the column
       "TRL own assessment"; incumbent technologies have TRL 9.
    2. The TRL is translated into a relative sd with the AACE cost estimate
       classes in ``TRL_SD_translation.csv`` (TRL 9 -> 10 %, ..., TRL 0 -> 100 %).
"""

from pathlib import Path

import numpy as np
import pandas as pd

from .raw_data import (
    raise_if_missing,
    read_iea_trl,
    read_import_price_relative_sd,
    read_technology_table,
    read_trl_to_relative_sd,
)

#: Distance of the 5 % and 95 % quantile from the mean of a normal
#: distribution, in standard deviations.
Z_SCORE_95_PERCENT = 1.645
#: TRL of technologies marked as "Incumbent".
INCUMBENT_TRL = 9


def relative_sd_from_trl(
    technology_table: pd.DataFrame,
    iea_trl: pd.Series,
    trl_to_relative_sd: pd.Series,
) -> pd.DataFrame:
    """Relative sd of all technologies in ``technology_table`` from their TRL.

    Args:
        technology_table: Table of ``read_technology_table``.
        iea_trl: TRL per IEA technology name (lower case), see ``read_iea_trl``.
        trl_to_relative_sd: Relative sd per TRL, see ``read_trl_to_relative_sd``.

    Returns:
        Table indexed by technology with the columns ``trl``, ``relative_sd``
        and ``method``.
    """
    trl = technology_table.apply(lambda row: _get_trl(row, iea_trl), axis=1)
    return pd.DataFrame(
        {
            "trl": trl,
            "relative_sd": trl.map(trl_to_relative_sd),
            "method": "trl",
        }
    )


def _get_trl(row: pd.Series, iea_trl: pd.Series) -> int:
    """TRL of one technology: IEA value if available, otherwise own assessment."""
    iea_name = row["iea_name"]
    if isinstance(iea_name, str):
        trl_of_iea = iea_trl.get(iea_name.lower(), np.nan)
        if not pd.isna(trl_of_iea):
            return int(trl_of_iea)
        if iea_name == "Incumbent":
            return INCUMBENT_TRL
    if pd.isna(row["own_trl"]):
        raise ValueError(
            f"Technology {row.name!r} has neither a TRL in the IEA classification "
            "nor an own TRL assessment in Technology_classification.csv."
        )
    return int(row["own_trl"])


def technology_relative_sd(
    raw_folder: Path, technologies: list[str], method: str
) -> pd.DataFrame:
    """Relative sd, TRL and primary class of the given technologies.

    Args:
        raw_folder: Folder ``data/raw_data/05-mean_variance``.
        technologies: Technologies of the model.
        method: ``"trl"``, see the module docstring.

    Returns:
        Table indexed by technology with the columns ``relative_sd``, ``trl``,
        ``method`` and ``primary_class``.
    """
    technology_table = read_technology_table(raw_folder)
    raise_if_missing(technologies, technology_table.index, raw_folder / "Technology_classification.csv")
    technology_table = technology_table.loc[technologies]

    iea_trl = read_iea_trl(raw_folder)
    trl_to_relative_sd = read_trl_to_relative_sd(raw_folder)
    if method == "trl":
        result = relative_sd_from_trl(technology_table, iea_trl, trl_to_relative_sd)
    else:
        raise ValueError(
            f"{method!r} is not a valid method, use 'trl'."
        )

    result["primary_class"] = technology_table["primary_class"]
    return result


def import_price_relative_sd(raw_folder: Path, carriers: list[str]) -> pd.Series:
    """Relative sd of the import price of the given carriers.

    Args:
        raw_folder: Folder ``data/raw_data/05-mean_variance``.
        carriers: Carriers of the model.

    Returns:
        Relative sd indexed by carrier, in the order of ``carriers``.
    """
    relative_sd = read_import_price_relative_sd(raw_folder)
    raise_if_missing(
        carriers, relative_sd.index, raw_folder / "relative_sd_import_price.csv"
    )
    return relative_sd.loc[carriers]
