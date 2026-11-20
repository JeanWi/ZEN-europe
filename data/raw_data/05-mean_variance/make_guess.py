"""Generate guessed relative sds and correlation matrices of technology capex and import prices.

Writes next to this script:
- relative_sd_technology_guess.csv, correlation_technology_guess.csv
  (used with ``technology_relative_sd_source: guess``)
- relative_sd_import_price_guess.csv, correlation_import_price_guess.csv
  (used with ``import_price_relative_sd_source: guess``)
The values are rough guesses without data search. Run: python make_guess.py

Correlation = L L^T with ones on the diagonal, L = guessed loadings on common
cost drivers (row sum of squares <= 1) -> positive semi-definite by construction.
"""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).parent

# technology: (relative_sd, {factor: loading})
# factors: epc = large-project construction (steel, labour, EPC margins, interest)
#          mfg = mass manufacturing / global supply chain
#          pe = power electronics & electrochemistry, batt = Li-ion cells,
#          h2 = PEM/alkaline stacks & H2 balance of plant, wind, solar,
#          therm = turbines/large boilers, sboil = small/packaged boilers,
#          hp = heat pumps, ccs = CO2 capture, chem = chemical process plants,
#          ref = refinery equipment, steel = steel plants, cem = cement,
#          pipe = linear infrastructure, geo = underground/civil works,
#          hydro = hydro civil works, veh = road vehicles, ship = ships,
#          bio = biomass handling, ptx = novel power-to-X integration,
#          nuc = nuclear-specific
T = {
    # power
    "photovoltaics": (0.15, {"mfg": 0.5, "solar": 0.6, "pe": 0.3}),
    "wind_onshore": (0.15, {"mfg": 0.4, "wind": 0.7, "epc": 0.2}),
    "wind_offshore": (0.25, {"mfg": 0.3, "wind": 0.6, "epc": 0.4, "ship": 0.2}),
    "natural_gas_turbine": (0.12, {"epc": 0.4, "therm": 0.7}),
    "natural_gas_turbine_CCS": (0.35, {"epc": 0.4, "therm": 0.5, "ccs": 0.6}),
    "hard_coal_plant": (0.12, {"epc": 0.5, "therm": 0.7}),
    "lignite_coal_plant": (0.12, {"epc": 0.5, "therm": 0.7}),
    "oil_plant": (0.12, {"epc": 0.4, "therm": 0.7}),
    "biomass_plant": (0.18, {"epc": 0.4, "therm": 0.6, "bio": 0.4}),
    "biomass_plant_CCS": (0.40, {"epc": 0.4, "therm": 0.4, "bio": 0.3, "ccs": 0.6}),
    "waste_plant": (0.18, {"epc": 0.4, "therm": 0.6, "bio": 0.3}),
    "nuclear": (0.45, {"epc": 0.6, "therm": 0.2, "nuc": 0.7}),
    "reservoir_hydro": (0.30, {"epc": 0.5, "hydro": 0.7, "geo": 0.2}),
    "run-of-river_hydro": (0.25, {"epc": 0.5, "hydro": 0.7}),
    "pumped_hydro": (0.30, {"epc": 0.5, "hydro": 0.7, "geo": 0.2}),
    "fuel_cell": (0.35, {"mfg": 0.3, "pe": 0.4, "h2": 0.7}),
    # storage
    "battery": (0.25, {"mfg": 0.4, "pe": 0.4, "batt": 0.75}),
    "natural_gas_storage": (0.20, {"epc": 0.4, "geo": 0.8}),
    "salt_cavern_storage": (0.30, {"epc": 0.4, "geo": 0.8}),
    "carbon_storage": (0.45, {"epc": 0.3, "geo": 0.6, "ccs": 0.5}),
    "oil_storage": (0.12, {"epc": 0.6, "pipe": 0.3}),
    # transport infrastructure
    "power_line": (0.20, {"epc": 0.5, "pipe": 0.5}),
    "district_heating_grid": (0.20, {"epc": 0.5, "pipe": 0.6}),
    "natural_gas_pipeline": (0.15, {"epc": 0.5, "pipe": 0.8}),
    "oil_pipeline": (0.15, {"epc": 0.5, "pipe": 0.8}),
    "hydrogen_pipeline": (0.25, {"epc": 0.5, "pipe": 0.7, "h2": 0.2}),
    "carbon_pipeline": (0.30, {"epc": 0.5, "pipe": 0.7, "ccs": 0.3}),
    "ammonia_pipeline": (0.25, {"epc": 0.5, "pipe": 0.8}),
    "methanol_pipeline": (0.20, {"epc": 0.5, "pipe": 0.8}),
    "olefin_pipeline": (0.20, {"epc": 0.5, "pipe": 0.8}),
    "lng_terminal": (0.20, {"epc": 0.7, "chem": 0.3, "geo": 0.2}),
    # heat
    "natural_gas_boiler": (0.08, {"mfg": 0.4, "sboil": 0.8}),
    "oil_boiler": (0.08, {"mfg": 0.4, "sboil": 0.8}),
    "biomass_boiler": (0.12, {"mfg": 0.4, "sboil": 0.7, "bio": 0.3}),
    "electrode_boiler": (0.12, {"mfg": 0.4, "sboil": 0.6, "pe": 0.3}),
    "natural_gas_boiler_DH": (0.10, {"epc": 0.3, "sboil": 0.6, "therm": 0.4}),
    "oil_boiler_DH": (0.10, {"epc": 0.3, "sboil": 0.6, "therm": 0.4}),
    "hard_coal_boiler_DH": (0.10, {"epc": 0.4, "sboil": 0.4, "therm": 0.6}),
    "biomass_boiler_DH": (0.15, {"epc": 0.3, "sboil": 0.5, "therm": 0.4, "bio": 0.3}),
    "waste_boiler_DH": (0.15, {"epc": 0.3, "sboil": 0.4, "therm": 0.5, "bio": 0.3}),
    "electrode_boiler_DH": (0.12, {"epc": 0.3, "sboil": 0.5, "pe": 0.4}),
    "heat_pump": (0.15, {"mfg": 0.5, "hp": 0.75, "pe": 0.2}),
    "heat_pump_DH": (0.20, {"epc": 0.3, "mfg": 0.3, "hp": 0.7, "pe": 0.2}),
    # hydrogen, fuels and chemicals
    "electrolysis": (0.35, {"mfg": 0.3, "pe": 0.4, "h2": 0.75}),
    "SMR": (0.12, {"epc": 0.4, "chem": 0.75}),
    "SMR_CCS": (0.30, {"epc": 0.4, "chem": 0.6, "ccs": 0.5}),
    "haber_bosch": (0.15, {"epc": 0.4, "chem": 0.75}),
    "methanol_from_natural_gas": (0.12, {"epc": 0.4, "chem": 0.75}),
    "methanol_from_hydrogen": (0.35, {"epc": 0.4, "chem": 0.6, "ptx": 0.5}),
    "methanol_from_biomass": (0.35, {"epc": 0.4, "chem": 0.5, "bio": 0.5}),
    "methanation": (0.35, {"epc": 0.3, "chem": 0.5, "ptx": 0.6}),
    "fischer_tropsch": (0.40, {"epc": 0.4, "chem": 0.5, "ptx": 0.5, "ref": 0.2}),
    "gasification": (0.40, {"epc": 0.4, "chem": 0.5, "bio": 0.5}),
    "pyrolysis": (0.40, {"epc": 0.3, "chem": 0.5, "bio": 0.5}),
    "anaerobic_digestion": (0.20, {"epc": 0.3, "mfg": 0.2, "bio": 0.7}),
    "biomethane_conversion": (0.20, {"epc": 0.3, "chem": 0.3, "bio": 0.6}),
    "refining": (0.12, {"epc": 0.4, "chem": 0.4, "ref": 0.7}),
    "oil_to_diesel_conversion": (0.12, {"epc": 0.4, "chem": 0.4, "ref": 0.7}),
    "oil_to_gasoline_conversion": (0.12, {"epc": 0.4, "chem": 0.4, "ref": 0.7}),
    "oil_to_kerosene_conversion": (0.12, {"epc": 0.4, "chem": 0.4, "ref": 0.7}),
    "oil_to_naphtha_conversion": (0.12, {"epc": 0.4, "chem": 0.4, "ref": 0.7}),
    "olefin_from_naphtha": (0.12, {"epc": 0.4, "chem": 0.6, "ref": 0.4}),
    "olefin_from_methanol": (0.25, {"epc": 0.4, "chem": 0.7, "ptx": 0.2}),
    "industrial_gas_consumer": (0.15, {"epc": 0.4, "sboil": 0.4, "chem": 0.3}),
    "DAC": (0.60, {"mfg": 0.3, "ccs": 0.5, "ptx": 0.4}),
    # steel and cement
    "BF_BOF": (0.10, {"epc": 0.5, "steel": 0.75}),
    "BF_BOF_CCS": (0.40, {"epc": 0.4, "steel": 0.5, "ccs": 0.6}),
    "EAF": (0.12, {"epc": 0.4, "steel": 0.6, "pe": 0.2}),
    "NG_DRI": (0.15, {"epc": 0.4, "steel": 0.7, "chem": 0.2}),
    "NG_DRI_CCS": (0.30, {"epc": 0.4, "steel": 0.6, "ccs": 0.5}),
    "H2_DRI": (0.35, {"epc": 0.4, "steel": 0.6, "ptx": 0.4, "h2": 0.2}),
    "cement_kiln": (0.10, {"epc": 0.5, "cem": 0.75}),
    "cement_post_comb": (0.40, {"epc": 0.4, "cem": 0.4, "ccs": 0.7}),
    "coal_to_cement_fuel": (0.08, {"epc": 0.3, "cem": 0.8}),
    "biomass_to_cement_fuel": (0.15, {"epc": 0.3, "cem": 0.7, "bio": 0.3}),
    "waste_to_cement_fuel": (0.15, {"epc": 0.3, "cem": 0.7, "bio": 0.3}),
    "hydrogen_to_cement_fuel": (0.35, {"epc": 0.3, "cem": 0.6, "ptx": 0.4, "h2": 0.2}),
    # vehicles and ships
    # vehicles: the fleet capex is huge, so only the powertrain-related part is
    # uncertain (low sd) and the shared vehicle body makes them highly correlated
    "ICE_petrol": (0.03, {"mfg": 0.2, "veh": 0.97}),
    "ICE_diesel": (0.03, {"mfg": 0.2, "veh": 0.97}),
    "BEV": (0.06, {"mfg": 0.2, "veh": 0.85, "batt": 0.45}),
    "HDT_diesel": (0.03, {"mfg": 0.2, "veh": 0.9}),
    "HDT_BET": (0.08, {"mfg": 0.2, "veh": 0.75, "batt": 0.55}),
    "HDT_FCEV": (0.12, {"mfg": 0.2, "veh": 0.7, "h2": 0.6, "pe": 0.1}),
    "diesel_ICE_ship": (0.08, {"epc": 0.3, "ship": 0.85}),
    "methanol_ICE_ship": (0.20, {"epc": 0.3, "ship": 0.8, "ptx": 0.2}),
    "ammonia_ICE_ship": (0.35, {"epc": 0.3, "ship": 0.7, "ptx": 0.4}),
    "hydrogen_FC_ship": (0.45, {"epc": 0.2, "ship": 0.6, "h2": 0.6}),
}

# carrier: (relative_sd of the import price, {factor: loading})
# factors: energy = general fossil energy price level, oil = crude oil and products,
#          gas = natural gas / LNG, coal, h2 = low-carbon hydrogen and derivatives,
#          bio = biomass markets, steel = steel and other materials,
#          elec = electricity imports
# carriers that are not imported (demands, heat, transport services) get sd 0
C_ = {
    "crude_oil": (0.35, {"energy": 0.5, "oil": 0.85}),
    "oil": (0.35, {"energy": 0.5, "oil": 0.85}),
    "diesel": (0.30, {"energy": 0.5, "oil": 0.8}),
    "gasoline": (0.30, {"energy": 0.5, "oil": 0.8}),
    "kerosene": (0.30, {"energy": 0.5, "oil": 0.8}),
    "naphtha": (0.30, {"energy": 0.5, "oil": 0.75}),
    "natural_gas": (0.40, {"energy": 0.5, "gas": 0.85}),
    "lng": (0.40, {"energy": 0.5, "gas": 0.8}),
    "hard_coal": (0.30, {"energy": 0.5, "coal": 0.8}),
    "lignite": (0.10, {"energy": 0.2, "coal": 0.4}),
    "uranium": (0.30, {}),
    "electricity": (0.25, {"energy": 0.3, "gas": 0.5, "elec": 0.6}),
    "hydrogen": (0.35, {"energy": 0.2, "gas": 0.2, "h2": 0.85}),
    "ammonia": (0.30, {"energy": 0.3, "gas": 0.3, "h2": 0.7}),
    "methanol": (0.30, {"energy": 0.3, "gas": 0.3, "h2": 0.5, "oil": 0.2}),
    "olefin": (0.20, {"energy": 0.3, "oil": 0.5, "steel": 0.2}),
    "biomass": (0.20, {"energy": 0.2, "bio": 0.8}),
    "wet_biomass": (0.20, {"bio": 0.8}),
    "biomethane": (0.25, {"energy": 0.2, "gas": 0.3, "bio": 0.7}),
    "waste": (0.10, {"bio": 0.4}),
    "fuel_for_cement": (0.15, {"energy": 0.4, "coal": 0.4, "bio": 0.2}),
    "clinker": (0.15, {"energy": 0.3, "steel": 0.5}),
    "primary_steel": (0.15, {"energy": 0.3, "coal": 0.2, "steel": 0.8}),
    "secondary_steel": (0.15, {"energy": 0.2, "elec": 0.2, "steel": 0.8}),
    "carbon": (0.0, {}),
    "district_heat": (0.0, {}),
    "heat": (0.0, {}),
    "passenger_mileage": (0.0, {}),
    "truck_mileage": (0.0, {}),
    "shipping": (0.0, {}),
}


def write_guess(entries: dict, element: str, name: str) -> pd.DataFrame:
    """Write the relative sd and the correlation (L L^T, ones on the diagonal)."""
    elements = sorted(entries)
    factors = sorted({f for _, loads in entries.values() for f in loads})
    L = pd.DataFrame(0.0, index=elements, columns=factors)
    for e, (_, loads) in entries.items():
        for f, v in loads.items():
            L.loc[e, f] = v
    norm = np.sqrt((L**2).sum(axis=1))
    assert (norm <= 1.0 + 1e-9).all(), norm[norm > 1]
    C = L.values @ L.values.T
    np.fill_diagonal(C, 1.0)
    corr = pd.DataFrame(C.round(4), index=elements, columns=elements)
    assert np.linalg.eigvalsh(corr.values).min() > -1e-10
    corr.to_csv(OUT / f"correlation_{name}_guess.csv")
    pd.DataFrame(
        {element: elements, "relative_sd": [entries[e][0] for e in elements]}
    ).to_csv(OUT / f"relative_sd_{name}_guess.csv", index=False)
    print(f"{name}: {len(elements)} elements; min eig {np.linalg.eigvalsh(corr.values).min():.4f}")
    return corr


corr = write_guess(T, "technology", "technology")
for a, b in [("BEV", "HDT_BET"), ("electrolysis", "fuel_cell"), ("wind_onshore", "wind_offshore"),
             ("photovoltaics", "wind_onshore"), ("nuclear", "hard_coal_plant"), ("SMR", "haber_bosch"),
             ("photovoltaics", "nuclear"), ("battery", "BEV"), ("BEV", "ICE_petrol"), ("ICE_petrol", "ICE_diesel"), ("BEV", "photovoltaics")]:
    print(" ", a, b, corr.loc[a, b])
corr = write_guess(C_, "carrier", "import_price")
for a, b in [("crude_oil", "diesel"), ("natural_gas", "lng"), ("crude_oil", "natural_gas"), ("natural_gas", "electricity"),
             ("hydrogen", "ammonia"), ("natural_gas", "hydrogen"), ("biomass", "wet_biomass"), ("hard_coal", "natural_gas")]:
    print(" ", a, b, corr.loc[a, b])
