"""Correlation of the technology capex and the import prices.

Import prices (setting ``mean_variance.import_price_relative_sd_source``):
the matrix in ``correlation_import_price.csv`` (``historical``) or
``correlation_import_price_guess.csv`` (``guess``) is used as it is.

Technology capex (setting ``mean_variance.technology_relative_sd_source``):

``guess``: the matrix in ``correlation_technology_guess.csv`` is used as it is.

``trl``: technologies are assumed to be correlated if they belong to the same technology
class or use the same carriers (ported from ``calculate_correl_coeff.py`` of the
mean-variance paper). Every technology is described by a feature vector:

- ``PRIMARY_CLASS_WEIGHT`` for its primary technology class (column "Primary
  technology class" in Technology_classification.csv),
- ``CARRIER_WEIGHT`` for each of its input and output carriers in the model.
  Storage and transport technologies have no input or output carriers, so their
  reference carrier is used.

The correlation of two technologies is the cosine similarity of their feature
vectors::

    ρ(a, b) = v_a · v_b / (|v_a| · |v_b|)

Because all feature vectors are non-negative, the correlations are between 0
and 1, and the matrix is positive semi-definite (it is a Gram matrix of unit
vectors), as required for a correlation matrix.

Spatial correlation of the technology capex: the correlation of the capex of
one technology between two different locations, per technology, from
``spatial_correlation_technology.csv``. Technologies not in the file get the
setting ``mean_variance.technology_spatial_correlation_default``. The plugin
combines it with the matrix above (see ``variance_sources.py`` of the plugin).
"""

from pathlib import Path

import numpy as np
import pandas as pd

from .raw_data import (
    raise_if_missing,
    read_import_price_correlation,
    read_technology_correlation_guess,
    read_technology_spatial_correlation,
)

PRIMARY_CLASS_WEIGHT = 0.9
CARRIER_WEIGHT = 0.3


def technology_correlation(
    primary_class: pd.Series, technology_elements: dict
) -> pd.DataFrame:
    """Correlation matrix of technologies from their class and carriers.

    Args:
        primary_class: Primary technology class per technology. Its index
            defines the technologies and their order in the matrix.
        technology_elements: ZEN-creator technology objects by name (e.g.
            ``model.technologies``), used to look up their carriers.

    Returns:
        Symmetric correlation matrix (technology x technology) with ones on the
        diagonal.
    """
    technologies = list(primary_class.index)
    carriers = {
        name: carriers_of_technology(technology_elements[name]) for name in technologies
    }

    class_features = pd.get_dummies(primary_class).astype(float) * PRIMARY_CLASS_WEIGHT
    all_carriers = sorted({c for tech in technologies for c in carriers[tech]})
    carrier_features = pd.DataFrame(0.0, index=technologies, columns=all_carriers)
    for technology in technologies:
        carrier_features.loc[technology, carriers[technology]] = CARRIER_WEIGHT
    # prefix the carriers so that they cannot be confused with class names
    carrier_features = carrier_features.add_prefix("carrier: ")

    features = pd.concat([class_features, carrier_features], axis=1).values
    lengths = np.linalg.norm(features, axis=1, keepdims=True)
    # technologies without any feature keep a zero vector (correlation 0)
    unit_features = np.divide(
        features, lengths, out=np.zeros_like(features), where=lengths != 0
    )

    correlation = unit_features @ unit_features.T
    np.fill_diagonal(correlation, 1.0)
    return pd.DataFrame(correlation, index=technologies, columns=technologies)


def carriers_of_technology(technology) -> list[str]:
    """Input and output carriers of a ZEN-creator technology.

    Conversion technologies have input and output carriers; storage and
    transport technologies only a reference carrier.
    """
    if hasattr(technology, "input_carrier") and hasattr(technology, "output_carrier"):
        carriers = list(technology.input_carrier.default_value or []) + list(
            technology.output_carrier.default_value or []
        )
    else:
        carriers = list(technology.reference_carrier.default_value or [])
    return sorted(set(carriers))


def technology_spatial_correlation(
    raw_folder: Path, technologies: list[str], default: float
) -> pd.Series:
    """Spatial correlation of the capex of the given technologies.

    Args:
        raw_folder: Folder ``data/raw_data/05-mean_variance``.
        technologies: Technologies of the model.
        default: Value for technologies that are not in the raw file.

    Returns:
        Spatial correlation indexed by technology, in the order of
        ``technologies``, between 0 and 1.
    """
    raw_values = read_technology_spatial_correlation(raw_folder)
    spatial_correlation = raw_values.reindex(technologies).fillna(default)
    outside = (spatial_correlation < 0) | (spatial_correlation > 1)
    if outside.any():
        raise ValueError(
            f"{raw_folder / 'spatial_correlation_technology.csv'} has "
            f"spatial_correlation values outside [0, 1] for "
            f"{list(spatial_correlation.index[outside])}."
        )
    return spatial_correlation.rename("spatial_correlation")


def technology_correlation_guess(
    raw_folder: Path, technologies: list[str]
) -> pd.DataFrame:
    """Guessed correlation matrix of the capex of the given technologies.

    Args:
        raw_folder: Folder ``data/raw_data/05-mean_variance``.
        technologies: Technologies of the model.

    Returns:
        Symmetric correlation matrix (technology x technology) in the order of
        ``technologies``.
    """
    correlation = read_technology_correlation_guess(raw_folder)
    return correlation


def import_price_correlation(
    raw_folder: Path, carriers: list[str], source: str
) -> pd.DataFrame:
    """Correlation matrix of the import prices of the given carriers.

    Args:
        raw_folder: Folder ``data/raw_data/05-mean_variance``.
        carriers: Carriers of the model.
        source: ``"historical"`` or ``"guess"``, see the module docstring.

    Returns:
        Symmetric correlation matrix (carrier x carrier) in the order of
        ``carriers``. Empty cells are read as 0.
    """
    if source == "historical":
        correlation_file = raw_folder / "correlation_import_price.csv"
    elif source == "guess":
        correlation_file = raw_folder / "correlation_import_price_guess.csv"
    else:
        raise ValueError(
            f"{source!r} is not a valid source, use 'historical' or 'guess'."
        )
    correlation = read_import_price_correlation(correlation_file)
    raise_if_missing(carriers, correlation.index, correlation_file)
    raise_if_missing(carriers, correlation.columns, correlation_file)
    correlation = correlation.loc[carriers, carriers].fillna(0.0)
    if not np.allclose(correlation.values, correlation.values.T):
        raise ValueError(
            f"The correlation matrix in {correlation_file} is not symmetric."
        )
    return correlation
