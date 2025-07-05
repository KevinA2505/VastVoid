# New faction-aware generic structures

import random
import math
from dataclasses import dataclass, field
from typing import Any

import pygame
import config

from fraction import Fraction, Color


@dataclass
class FactionStructure:
    """Base structure that can adopt traits based on a faction."""

    name: str
    fraction: Fraction | None = None
    modules: list[str] = field(default_factory=list)
    color: Color | None = None
    shape: str | None = None
    aura: str | None = None

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        """Configure this structure with properties for ``fraction``.

        Subclasses should override this method to apply specific
        modifications like additional modules or stat bonuses.
        """
        self.fraction = fraction
        self.color = fraction.color
        self.shape = fraction.shape
        self.aura = fraction.aura


@dataclass
class CapitalShip(FactionStructure):
    """Large mobile base acting as the heart of a faction."""
    x: float = 0.0
    y: float = 0.0
    hull: int = 1000
    hangar_capacity: int = 4
    energy_sources: list[Any] = field(default_factory=list)

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        if fraction.name == "Solar Dominion":
            self.hull = 1500
            self.modules.extend(["Heavy Cannons", "Fighter Bays"])
        elif fraction.name == "Cosmic Guild":
            self.hull = 1200
            self.modules.extend(["Trade Hub", "Drone Bays"])
        elif fraction.name == "Nebula Order":
            self.hull = 1100
            self.modules.extend(["Research Labs", "Sensor Array"])
        elif fraction.name == "Pirate Clans":
            self.hull = 1000
            self.modules.extend(["Cloaking Device", "Raider Hangars"])
        elif fraction.name == "Free Explorers":
            self.hull = 1300
            self.modules.extend(["Survey Deck", "Jump Drives"])

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        color = self.color if self.color else (200, 200, 200)
        size = 20
        x = int((self.x - offset_x) * zoom)
        y = int((self.y - offset_y) * zoom)
        scaled = int(size * zoom)
        if self.shape == "angular":
            points = [
                (x - scaled, y - scaled),
                (x + scaled, y - scaled),
                (x + scaled, y + scaled),
                (x - scaled, y + scaled),
            ]
            pygame.draw.polygon(screen, color, points)
        elif self.shape == "spiky":
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = scaled if i % 2 == 0 else scaled // 2
                points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
            pygame.draw.polygon(screen, color, points)
        elif self.shape in {"sleek", "streamlined"}:
            rect = pygame.Rect(x - scaled, y - scaled // 2, scaled * 2, scaled)
            pygame.draw.ellipse(screen, color, rect)
        else:
            pygame.draw.circle(screen, color, (x, y), scaled)


@dataclass
class OrbitalPlatform(FactionStructure):
    """Modular station designed to be adapted per faction."""

    radius: int = 30
    defense_rating: int = 0

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation will add weapons or support modules.


@dataclass
class InfluenceBeacon(FactionStructure):
    """Beacon marking territory and granting bonuses to allies."""

    range: float = 500.0
    bonus: str | None = None

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation may set specific bonuses.


@dataclass
class PlanetOutpost(FactionStructure):
    """Small base used to claim planets or moons."""

    capacity: int = 10

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation may provide research or trade perks.


def spawn_capital_ships(fractions: list[Fraction], width: int, height: int) -> list[CapitalShip]:
    """Return one capital ship per faction placed randomly in the world."""
    ships = []
    for frac in fractions:
        ship = CapitalShip(name=f"{frac.name} Flagship")
        ship.apply_fraction_traits(frac)
        ship.x = random.randint(0, width)
        ship.y = random.randint(0, height)
        ships.append(ship)
    return ships
