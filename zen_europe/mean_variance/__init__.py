"""Input data of the ZEN-garden mean-variance plugin (uncertain costs).

See ``writer.py`` for the written files and ``relative_sd.py`` and
``correlation.py`` for how they are calculated.
"""

from .writer import write_mean_variance_files

__all__ = ["write_mean_variance_files"]
