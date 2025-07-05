# New faction-aware generic structures

from dataclasses import dataclass, field
from typing import Any, Tuple

from fraction import Fraction


@dataclass
class FactionStructure:
    """Base structure that can adopt traits based on a faction.

    The fields ``color``, ``size`` and ``aura`` allow each structure to
    display a distinct identity once a faction is applied.
    """

    name: str
    color: Tuple[int, int, int] = (255, 255, 255)
    size: int = 1
    aura: str | None = None
    fraction: Fraction | None = None
    modules: list[str] = field(default_factory=list)

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        """Configure this structure with properties for ``fraction``.

        Subclasses may set attributes such as ``color`` or ``aura`` to
        visually represent the faction's identity.
        """
        self.fraction = fraction


@dataclass
class CapitalShip(FactionStructure):
    """Large mobile base acting as the heart of a faction."""

    hull: int = 1000
    hangar_capacity: int = 4
    color: Tuple[int, int, int] = (240, 80, 40)
    size: int = 100
    aura: str | None = "command"
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
    color: Tuple[int, int, int] = (80, 80, 240)
    size: int = 40
    aura: str | None = "industrial"

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation will add weapons or support modules.


@dataclass
class InfluenceBeacon(FactionStructure):
    """Beacon marking territory and granting bonuses to allies."""

    range: float = 500.0
    bonus: str | None = None
    color: Tuple[int, int, int] = (200, 200, 50)
    size: int = 10
    aura: str | None = "influence"

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation may set specific bonuses.


@dataclass
class PlanetOutpost(FactionStructure):
    """Small base used to claim planets or moons."""

    capacity: int = 10
    color: Tuple[int, int, int] = (120, 120, 120)
    size: int = 15
    aura: str | None = "settlement"

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Future implementation may provide research or trade perks.
