from typing import ClassVar

from pydantic import Field
from zen_creator.utils.settings import SettingsCategory


class RegionSettings(SettingsCategory):
    """Spatial scope of the model."""

    name: ClassVar[str] = "region"
    controls: ClassVar[dict[str, str]] = {"set_nodes": "system.set_nodes"}

    set_nodes: list[str] = Field(
        default_factory=lambda: [
            "AT",
            "BE",
            "BG",
            "CH",
            "CZ",
            "DE",
            "DK",
            "EE",
            "EL",
            "ES",
            "FI",
            "FR",
            "HR",
            "HU",
            "IE",
            "IT",
            "LT",
            "LU",
            "LV",
            "NL",
            "NO",
            "PL",
            "PT",
            "RO",
            "SE",
            "SI",
            "SK",
            "UK",
        ]
    )
