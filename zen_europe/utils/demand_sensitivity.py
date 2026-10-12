"""Demand sensitivity scenarios shared across the demand-carrying carriers.

Groups carriers into the economic sectors used by the demand sensitivity
analysis (`ScenarioSettings.sensitivity_demand`): every carrier of a sector
varies its demand together with the other carriers of that sector, by the
same generic factor.
"""

from zen_creator import Scenario

# generic demand variation factors
FACTOR_LOW_DEMAND_GENERIC = 0.75
FACTOR_HIGH_DEMAND_GENERIC = 1.25

# carriers grouped by the economic sector they vary demand together with
DEMAND_SENSITIVITY_SECTORS: dict[str, list[str]] = {
    "electricity_heat": ["electricity", "heat"],
    "transport": ["passenger_mileage", "truck_mileage", "kerosene", "shipping"],
    "industry": [
        "primary_steel",
        "secondary_steel",
        "clinker",
        "olefin",
        "ammonia",
        "methanol",
    ],
}

_CARRIER_SECTORS = {
    carrier: sector
    for sector, carriers in DEMAND_SENSITIVITY_SECTORS.items()
    for carrier in carriers
}


def demand_sensitivity_scenarios(carrier_name: str) -> list[Scenario]:
    """Return the low and high demand scenarios of a carrier's sector.

    Args:
        carrier_name: Name of the carrier, e.g. 'electricity'.

    Returns:
        list[Scenario]: The 'low' and 'high' demand scenario of the carrier's
            sector, applied as a factor on the demand.

    Raises:
        KeyError: If the carrier is not part of a demand sensitivity sector.
    """
    sector = _CARRIER_SECTORS[carrier_name]
    return [
        Scenario(f"{sector}_low", suffix="low", file_op=FACTOR_LOW_DEMAND_GENERIC),
        Scenario(f"{sector}_high", suffix="high", file_op=FACTOR_HIGH_DEMAND_GENERIC),
    ]
