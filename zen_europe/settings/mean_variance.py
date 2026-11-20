from typing import ClassVar, Literal

from pydantic import Field
from zen_creator.utils.settings import SettingsCategory


class MeanVarianceSettings(SettingsCategory):
    """Settings for the input data of the ZEN-garden mean-variance plugin.

    When ``write_files`` is true, the folder ``mean_variance/`` with relative
    standard deviations and correlation matrices is written into the dataset
    (see ``zen_europe/mean_variance``). The raw data is in
    ``data/raw_data/05-mean_variance``.
    """

    name: ClassVar[str] = "mean_variance"

    write_files: bool = False

    # how the relative standard deviation and the correlation of the
    # technology capex are derived:
    # - "trl": sd from the technology readiness level (AACE cost estimate
    #   classes), correlation from technology class and carriers
    # - "guess": sd and correlation from the rough guesses in
    #   relative_sd_technology_guess.csv and correlation_technology_guess.csv
    technology_relative_sd_source: Literal["trl", "guess"] = "trl"

    # spatial correlation (correlation of the capex of one technology between
    # two locations) of technologies that are not listed in
    # spatial_correlation_technology.csv; 1 = same cost at all locations
    technology_spatial_correlation_default: float = Field(default=1.0, ge=0, le=1)
