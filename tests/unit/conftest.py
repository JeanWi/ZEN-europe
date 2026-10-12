"""Shared pytest fixtures for unit tests."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest
from zen_creator import Dataset, DatasetCollection, Model


@pytest.fixture(autouse=True)
def reset_singleton_registries() -> Iterator[None]:
    """Reset dataset registries for test isolation."""
    Dataset._registries.clear()
    DatasetCollection._registries.clear()
    yield
    Dataset._registries.clear()
    DatasetCollection._registries.clear()


RAW_DATA_PATH = Path(__file__).parents[2] / "data" / "raw_data"


@pytest.fixture
def model(tmp_path: Path, request: pytest.FixtureRequest) -> Model:
    """Create a minimal model object that is sufficient for element tests.

    The element ``write()`` path resolution requires ``output_folder`` and
    ``name`` to be defined, while templates using datasets require
    ``source_path``.

    ``source_path`` points at the raw data so that datasets read their cached
    series instead of downloading them. It falls back to ``tmp_path`` when the
    raw data has not been unpacked, in which case datasets without a cache
    reach out to their source.
    """
    model = Model()
    model.name = f"{request.module.__name__.split('.')[-1]}_model"
    model.output_folder = tmp_path / "outputs"
    model.source_path = RAW_DATA_PATH if RAW_DATA_PATH.exists() else tmp_path
    return model
