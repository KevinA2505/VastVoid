from dataclasses import dataclass
from typing import List

@dataclass
class Biome:
    """Basic information about a planetary biome."""
    color: tuple[int, int, int]
    spawn_items: List[str]
    spawn_rate: float  # probability [0,1] of item spawn per patch
    patch_scale: float = 1.0


BIOMES: dict[str, Biome] = {
    # Lush vegetation with a good amount of collectibles
    "forest": Biome(
        (50, 120, 50),
        ["flor eterea", "pluma de fenix", "gema de alma"],
        0.15,
        1.2,
    ),
    # Arid landscapes rich in ancient artefacts
    "desert": Biome(
        (210, 200, 150),
        ["arena del tiempo", "fragmento de meteorito", "mapa estelar antiguo"],
        0.15,
        1.0,
    ),
    # Frozen plains with valuable energy sources
    "ice world": Biome(
        (220, 235, 245),
        ["helio-3", "cristal quantico", "huevo de dragon", "cristal de energia"],
        0.15,
        1.0,
    ),
    # Volcanic regions containing rare minerals
    "lava": Biome(
        (150, 60, 30),
        ["plutonio", "antimateria", "corazon de estrella"],
        0.1,
        0.8,
    ),
    # Deep oceans with strange curiosities
    "ocean world": Biome(
        (30, 80, 160),
        ["hidrogeno liquido", "vapor condensado", "lagrima de sirena"],
        0.15,
        1.3,
    ),
    # Colourful reefs hiding unique resources
    "coral reef": Biome(
        (80, 150, 200),
        ["coral brillante", "perla abisal"],
        0.2,
        1.1,
    ),
    # Darker deep sea trenches
    "deep sea": Biome(
        (20, 40, 90),
        ["cristal de energia", "lagrima de sirena"],
        0.12,
        1.3,
    ),
    # Default rocky surfaces
    "rocky": Biome(
        (110, 110, 110),
        ["hierro", "cobre", "cuarzo"],
        0.12,
        0.9,
    ),
}
