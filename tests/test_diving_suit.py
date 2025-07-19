import types
import pygame
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from planet_surface import PlanetSurface
from character import Player, Human
from fraction import FRACTIONS

pygame.init()

class DummyPlanet:
    def __init__(self):
        self.environment = "ocean world"
        self.biomes = ["ocean world"]

def test_diving_suit_allows_water_walk():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    planet = DummyPlanet()
    surface = PlanetSurface(planet, player)
    # find a water cell
    wx = wy = None
    for x in range(0, surface.width, 30):
        for y in range(0, surface.height, 30):
            if surface.is_water(x, y):
                wx, wy = x, y
                break
        if wx is not None:
            break
    assert wx is not None, "no water found"
    assert not surface.is_walkable(wx, wy)
    player.add_item("traje de buceo")
    assert surface.is_walkable(wx, wy)
