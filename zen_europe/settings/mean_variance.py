from typing import ClassVar, Literal

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

    # how the relative standard deviation of the technology capex is derived:
    # - "trl": from the technology readiness level (AACE cost estimate classes)
    technology_relative_sd_source: Literal["trl"] = "trl"
