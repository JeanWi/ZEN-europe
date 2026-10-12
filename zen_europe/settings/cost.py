from typing import ClassVar

from zen_creator.utils.settings import SettingsCategory


class CostSettings(SettingsCategory):
    """Cost-related settings."""

    name: ClassVar[str] = "cost"

    use_learning_curves: bool = True
    use_nodal_biomass_prices: bool = False
    assume_oil_price_for_diesel_and_gasoline: bool = False
