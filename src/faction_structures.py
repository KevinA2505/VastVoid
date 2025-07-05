# New faction-aware generic structures

from dataclasses import dataclass, field
from typing import Any

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

    hull: int = 1000
    hangar_capacity: int = 4
    energy_sources: list[Any] = field(default_factory=list)

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation will modify hull or modules depending
        # on the owning faction.


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
