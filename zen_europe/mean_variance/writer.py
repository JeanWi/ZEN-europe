"""Write the input files of the ZEN-garden mean-variance plugin into a dataset.

Output (read by ``zen_garden_plugins.mean_variance_optimization`` in
ZEN-galaxies)::

    <dataset>/mean_variance/
        README.md
        technology_capex/relative_sd.csv   technology, relative_sd, trl, method
        technology_capex/correlation.csv   technology x technology
        technology_capex/spatial_correlation.csv   technology, spatial_correlation
        imports/relative_sd.csv           carrier, relative_sd
        imports/correlation.csv            carrier x carrier

Every technology and carrier of the model is written. If the raw data lacks
one of them, an error lists the missing elements.
"""

import logging
from pathlib import Path

import pandas as pd

from .correlation import (
    import_price_correlation,
    technology_correlation,
    technology_correlation_guess,
    technology_spatial_correlation,
)
from .relative_sd import import_price_relative_sd, technology_relative_sd

logger = logging.getLogger(__name__)

OUTPUT_FOLDER_NAME = "mean_variance"
RAW_DATA_FOLDER = "05-mean_variance"

#: Decimals of the written correlations.
CORRELATION_DECIMALS = 10


def write_mean_variance_files(model) -> Path:
    """Write the mean-variance input files for all elements of ``model``.

    Must be called after ``model.write()``, which deletes the output folder.

    Returns:
        The written ``mean_variance`` folder.
    """
    settings = model.settings.mean_variance
    raw_folder = model.source_path / RAW_DATA_FOLDER
    output_folder = Path(model.output_path) / OUTPUT_FOLDER_NAME

    # TECHNOLOGIES
    technologies = sorted(model.technologies)
    technology_sd = technology_relative_sd(
        raw_folder, technologies, settings.technology_relative_sd_source
    )
    if settings.technology_relative_sd_source == "guess":
        technology_correlation_matrix = technology_correlation_guess(
            raw_folder, technologies
        )
    else:
        technology_correlation_matrix = technology_correlation(
            technology_sd["primary_class"], model.technologies
        )
    _write_variance(
        output_folder / "technology_capex",
        technology_sd[["relative_sd", "trl", "method"]].rename_axis("technology"),
        technology_correlation_matrix,
    )
    spatial_correlation = technology_spatial_correlation(
        raw_folder, technologies, settings.technology_spatial_correlation_default
    )
    spatial_correlation.rename_axis("technology").to_frame().to_csv(
        output_folder / "technology_capex" / "spatial_correlation.csv"
    )

    # IMPORTS
    carriers = sorted(model.carriers)
    import_sd = import_price_relative_sd(
        raw_folder, carriers, settings.import_price_relative_sd_source
    )
    import_correlation = import_price_correlation(
        raw_folder, carriers, settings.import_price_relative_sd_source
    )
    _write_variance(
        output_folder / "imports",
        import_sd.to_frame("relative_sd").rename_axis("carrier"),
        import_correlation,
    )

    _write_readme(
        output_folder,
        settings.technology_relative_sd_source,
        settings.technology_spatial_correlation_default,
        settings.import_price_relative_sd_source,
    )
    logger.info(f"Wrote mean-variance input files to {output_folder}")
    return output_folder


def _write_variance(
    folder: Path, relative_sd: pd.DataFrame, correlation: pd.DataFrame
) -> None:
    """Write ``relative_sd.csv`` and ``correlation.csv`` of one variance source."""
    folder.mkdir(parents=True, exist_ok=True)
    relative_sd.to_csv(folder / "relative_sd.csv")
    # the top-left cell of the matrix stays empty: the plugin uses the row and
    # column labels as coordinates and fails if the index has a name
    correlation = correlation.rename_axis(index=None, columns=None)
    correlation.round(CORRELATION_DECIMALS).to_csv(folder / "correlation.csv")


def _write_readme(
    output_folder: Path,
    technology_method: str,
    spatial_correlation_default: float,
    import_price_source: str,
) -> None:
    """Explain the files of the ``mean_variance`` folder."""
    readme = f"""# Input data of the mean-variance plugin

Written by ZEN-Europe (`zen_europe/mean_variance`) from the raw data in
`data/raw_data/05-mean_variance`. Read by the ZEN-garden plugin
`mean_variance_optimization` (ZEN-galaxies).

## technology_capex/
- `relative_sd.csv`: standard deviation of the specific capex as a share of the
  capex (0.1 = 10 %), per technology.
  - `trl`: technology readiness level
  - `method`: how `relative_sd` was derived. This dataset uses the setting
    `{technology_method}`: `trl` = from the TRL via the AACE cost estimate
    classes, `guess` = rough guesses from `relative_sd_technology_guess.csv`
- `correlation.csv`: correlation of the capex between technologies. `trl`:
  cosine similarity of their technology class and input/output carriers;
  `guess`: rough guesses from `correlation_technology_guess.csv`.
- `spatial_correlation.csv`: correlation of the capex of one technology between
  two different locations (1 = same cost at all locations, 0 = independent).
  From `spatial_correlation_technology.csv`; technologies not listed there get
  {spatial_correlation_default}.

## imports/
- `relative_sd.csv`: standard deviation of the import price as a share of the
  price, per carrier.
- `correlation.csv`: correlation of the import prices between carriers.

This dataset uses the setting `{import_price_source}`: `historical` =
hand-set values from `relative_sd_import_price.csv` and
`correlation_import_price.csv`, `guess` = rough guesses from
`relative_sd_import_price_guess.csv` and `correlation_import_price_guess.csv`.

All entries of the same technology or carrier at the same location (years,
capacity types, time steps) are assumed to be perfectly correlated. Between
locations, technologies use `spatial_correlation`; carriers are perfectly
correlated.
"""
    (output_folder / "README.md").write_text(readme, encoding="utf-8")
