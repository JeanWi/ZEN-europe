from zen_creator import Sector

from zen_europe.elements.carriers.lng import LNG
from zen_europe.elements.carriers.natural_gas import NaturalGas
from zen_europe.elements.conversion_technologies.lng_terminal import LNGTerminal
from zen_europe.elements.storage_technologies.natural_gas_storage import (
    NaturalGasStorage,
)
from zen_europe.elements.transport_technologies.natural_gas_pipeline import (
    NaturalGasPipeline,
)


class GasSector(Sector):
    """Natural gas import, storage and transport."""

    name = "gas"
    required_sectors = []

    def __init__(self) -> None:
        super().__init__()
        self.elements = [
            LNGTerminal,
            NaturalGasPipeline,
            NaturalGasStorage,
            LNG,
            NaturalGas,
        ]
