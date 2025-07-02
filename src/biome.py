from dataclasses import dataclass
from typing import List

@dataclass
class Biome:
    """Basic information about a planetary biome."""
    color: tuple[int, int, int]
    spawn_items: List[str]
    spawn_rate: float  # probability [0,1] of item spawn per patch


BIOMES: dict[str, Biome] = {
    "forest": Biome((50, 120, 50), ["flor eterea"], 0.05),
    "desert": Biome((210, 200, 150), ["arena del tiempo"], 0.05),
    "ice": Biome((220, 235, 245), ["helio-3"], 0.05),
}
