from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from zen_europe.datasets.datasets.technology.scigrid import SciGridIGGIELGNC1

if TYPE_CHECKING:
    from zen_creator.model import Model

from zen_creator.datasets.datasets.metadata import AssumptionInformation
from zen_creator.elements import StorageTechnology
from zen_creator.utils.attribute import Attribute


class NaturalGasStorage(StorageTechnology):
    """Class containing all data and assumptions for natural gas storage
    technology."""

    name: str = "natural_gas_storage"

    # round-trip efficiency, split evenly between charging and discharging
    EFFICIENCY_ROUND_TRIP = 0.995

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """
        Sets the reference carrier of natural gas storage to natural gas.
        """
        return Attribute(
            name="reference_carrier", default_value=["natural_gas"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        """
        Sets the lifetime of natural gas storage.
        """
        attr = self.lifetime
        return attr.set_data(
            default_value=200,
            source=AssumptionInformation(
                description=(
                    "The lifetime of natural gas storage is manually set to "
                    "200 years. Only the existing storages are modeled, which "
                    "do not retire within the modeling horizon."
                ),
            ),
        )

    def _set_efficiency_charge(self) -> Attribute:
        """
        Sets the charging efficiency of natural gas storage.
        """
        attr = self.efficiency_charge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=AssumptionInformation(
                description=(
                    "The round-trip efficiency of natural gas storage is "
                    f"manually set to {self.EFFICIENCY_ROUND_TRIP}, "
                    "and is split evenly between charging and discharging."
                ),
            ),
        )

    def _set_efficiency_discharge(self) -> Attribute:
        """
        Sets the discharging efficiency of natural gas storage.
        """
        attr = self.efficiency_discharge
        return attr.set_data(
            default_value=np.sqrt(self.EFFICIENCY_ROUND_TRIP),
            source=AssumptionInformation(
                description=(
                    "The round-trip efficiency of natural gas storage is "
                    f"manually set to {self.EFFICIENCY_ROUND_TRIP}, "
                    "and is split evenly between charging and discharging."
                ),
            ),
        )

    def _set_capacity_limit(self) -> Attribute:
        """
        Sets the power capacity limit of natural gas storage.
        """
        attr = self.capacity_limit
        return attr.set_data(
            default_value=0,
            source=AssumptionInformation(
                description=(
                    "No new natural gas storage can be built, so the power "
                    "capacity limit is manually set to 0."
                ),
            ),
        )

    def _set_capacity_limit_energy(self) -> Attribute:
        """
        Sets the energy capacity limit of natural gas storage.
        """
        attr = self.capacity_limit_energy
        return attr.set_data(
            default_value=0,
            source=AssumptionInformation(
                description=(
                    "No new natural gas storage can be built, so the energy "
                    "capacity limit is manually set to 0."
                ),
            ),
        )

    def _set_capex_specific_storage(self) -> Attribute:
        """
        Sets the power-specific capex of natural gas storage.
        """
        attr = self.capex_specific_storage
        return attr.set_data(
            default_value=0,
            source=AssumptionInformation(
                description=(
                    "The power-specific capex of natural gas storage is "
                    "manually set to 0, as only the existing storages are "
                    "modeled."
                ),
            ),
        )

    def _set_capex_specific_storage_energy(self) -> Attribute:
        """
        Sets the energy-specific capex of natural gas storage.
        """
        attr = self.capex_specific_storage_energy
        return attr.set_data(
            default_value=0,
            source=AssumptionInformation(
                description=(
                    "The energy-specific capex of natural gas storage is "
                    "manually set to 0, as only the existing storages are "
                    "modeled."
                ),
            ),
        )

    def _set_capacity_existing(self) -> Attribute:
        """
        Sets the existing power capacity of natural gas storage.
        """
        if not self.settings.investment.use_existing_capacities:
            return self.capacity_existing.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description="We do not consider existing capacities.",
                ),
            )
        scigrid = SciGridIGGIELGNC1(source_path=self.source_path)
        return scigrid.get_capacity_existing(self)

    def _set_capacity_existing_energy(self) -> Attribute:
        """
        Sets the existing energy capacity of natural gas storage.
        """
        if not self.settings.investment.use_existing_capacities:
            return self.capacity_existing_energy.set_data(
                default_value=0,
                df=None,
                source=AssumptionInformation(
                    description="We do not consider existing capacities.",
                ),
            )
        scigrid = SciGridIGGIELGNC1(source_path=self.source_path)
        return scigrid.get_capacity_existing(self, power=False)
