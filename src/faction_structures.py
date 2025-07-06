# New faction-aware generic structures

import random
import math
from dataclasses import dataclass, field
from typing import Any
from star import Star

import pygame

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
class ChannelArm:
    """Simple helper representing an energy channel arm."""

    angle: float
    length: float
    target: Star | None = None


@dataclass
class CapitalShip(FactionStructure):
    """Large mobile base acting as the heart of a faction."""

    x: float = 0.0
    y: float = 0.0
    hull: int = 1000
    hangar_capacity: int = 4
    energy_sources: list[Any] = field(default_factory=list)
    radius: int = 50
    aura_radius: int = 80
    arms: list[ChannelArm] = field(default_factory=list)

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        if fraction.name == "Solar Dominion":
            self.hull = 1500
            self.modules.extend(["Heavy Cannons", "Fighter Bays"])
            self.aura_radius = 120
            self.radius = max(self.radius, self.aura_radius)
            self.arms = [
                ChannelArm(i * 2 * math.pi / 5, self.radius)
                for i in range(5)
            ]
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

    def update(self, dt: float, sectors: list) -> None:
        if not (self.fraction and self.fraction.name == "Solar Dominion"):
            return
        stars: list[Star] = []
        for sec in sectors:
            for system in sec.systems:
                stars.append(system.star)
        used = set()
        for arm in self.arms:
            nearest = None
            min_d = float("inf")
            for star in stars:
                if star in used and star is not arm.target:
                    continue
                d = math.hypot(star.x - self.x, star.y - self.y)
                if d < min_d:
                    min_d = d
                    nearest = star
            if nearest:
                arm.target = nearest
                used.add(nearest)
            if arm.target:
                tx = arm.target.x
                ty = arm.target.y
                targ_angle = math.atan2(ty - self.y, tx - self.x)
                diff = (targ_angle - arm.angle + math.pi) % (2 * math.pi) - math.pi
                rotate = 1.5 * dt
                if abs(diff) < rotate:
                    arm.angle = targ_angle
                else:
                    arm.angle += rotate if diff > 0 else -rotate
                arm.angle %= 2 * math.pi

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        color = self.color if self.color else (200, 200, 200)
        outline = tuple(max(0, c - 60) for c in color)
        blink = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 300.0)
        flash = tuple(min(255, int(c + 100 * blink)) for c in color)
        size = 150  # increased size for more imposing ships
        x = int((self.x - offset_x) * zoom)
        y = int((self.y - offset_y) * zoom)
        scaled = int(size * zoom)
        if self.fraction and self.fraction.name == "Solar Dominion":
            body = [
                (x, y - scaled // 2),
                (x + scaled // 2, y + scaled // 2),
                (x - scaled // 2, y + scaled // 2),
            ]
            pygame.draw.polygon(screen, color, body)
            pygame.draw.polygon(screen, outline, body, max(1, int(2 * zoom)))
            spike = scaled // 5
            left_spike = [
                (x - scaled // 2, y + scaled // 2),
                (x - scaled // 2 - spike, y + scaled // 2),
                (x - scaled // 2, y + scaled // 2 - spike),
            ]
            right_spike = [
                (x + scaled // 2, y + scaled // 2),
                (x + scaled // 2 + spike, y + scaled // 2),
                (x + scaled // 2, y + scaled // 2 - spike),
            ]
            pygame.draw.polygon(screen, color, left_spike)
            pygame.draw.polygon(screen, color, right_spike)
            pygame.draw.polygon(screen, outline, left_spike, max(1, int(2 * zoom)))
            pygame.draw.polygon(screen, outline, right_spike, max(1, int(2 * zoom)))
            thr = scaled // 4
            thr_rect = pygame.Rect(x - thr // 2, y + scaled // 2 - thr // 2, thr, thr)
            pygame.draw.rect(screen, color, thr_rect)
            pygame.draw.rect(screen, outline, thr_rect, max(1, int(2 * zoom)))
            aura_r = int(self.aura_radius * zoom)
            if aura_r > 0:
                aura = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(aura, (255, 255, 255, 40), (aura_r, aura_r), aura_r)
                screen.blit(aura, (x - aura_r, y - aura_r))
            for arm in self.arms:
                arm_x = x + int(math.cos(arm.angle) * arm.length * zoom)
                arm_y = y + int(math.sin(arm.angle) * arm.length * zoom)
                pygame.draw.rect(screen, color, (arm_x - 2, arm_y - 2, 4, 4))
                if arm.target:
                    end = (
                        int((arm.target.x - offset_x) * zoom),
                        int((arm.target.y - offset_y) * zoom),
                    )
                    pygame.draw.line(
                        screen, (255, 255, 100), (arm_x, arm_y), end, max(1, int(2 * zoom))
                    )
            lights = [
                (x, y - scaled // 3),
                (x, y + scaled // 2 + thr // 2),
            ]
            for lx, ly in lights:
                pygame.draw.circle(screen, flash, (lx, ly), max(2, int(3 * zoom)))
        elif self.shape == "angular":
            # square hull with triangular wings
            hull = pygame.Rect(x - scaled // 2, y - scaled // 2, scaled, scaled)
            pygame.draw.rect(screen, color, hull)
            pygame.draw.rect(screen, outline, hull, max(1, int(2 * zoom)))
            left_wing = [
                (x - scaled // 2, y),
                (x - scaled, y - scaled // 2),
                (x - scaled, y + scaled // 2),
            ]
            right_wing = [
                (x + scaled // 2, y),
                (x + scaled, y - scaled // 2),
                (x + scaled, y + scaled // 2),
            ]
            pygame.draw.polygon(screen, color, left_wing)
            pygame.draw.polygon(screen, color, right_wing)
            pygame.draw.polygon(screen, outline, left_wing, max(1, int(2 * zoom)))
            pygame.draw.polygon(screen, outline, right_wing, max(1, int(2 * zoom)))
            for lx, ly in [
                (x - scaled // 2, y),
                (x + scaled // 2, y),
            ]:
                pygame.draw.circle(screen, flash, (lx, ly), max(2, int(3 * zoom)))
        elif self.shape == "spiky":
            # star shape with a central core
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                r = scaled if i % 2 == 0 else scaled // 2
                points.append((x + r * math.cos(angle), y + r * math.sin(angle)))
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, outline, points, max(1, int(2 * zoom)))
            pygame.draw.circle(screen, color, (x, y), scaled // 2)
            pygame.draw.circle(screen, outline, (x, y), scaled // 2, max(1, int(2 * zoom)))
            pygame.draw.circle(screen, flash, (x, y), max(2, int(3 * zoom)))
        elif self.shape in {"sleek", "streamlined"}:
            # long ellipse with nose and small wings
            rect = pygame.Rect(
                x - scaled, y - scaled // 3, scaled * 2, int(scaled / 1.5)
            )
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.ellipse(screen, outline, rect, max(1, int(2 * zoom)))
            nose = [
                (x + scaled, y),
                (x + scaled + scaled // 2, y - scaled // 4),
                (x + scaled + scaled // 2, y + scaled // 4),
            ]
            wing_top = [
                (x - scaled // 2, y - scaled // 6),
                (x, y - scaled // 2),
                (x + scaled // 2, y - scaled // 6),
            ]
            wing_bottom = [
                (x - scaled // 2, y + scaled // 6),
                (x, y + scaled // 2),
                (x + scaled // 2, y + scaled // 6),
            ]
            pygame.draw.polygon(screen, color, nose)
            pygame.draw.polygon(screen, color, wing_top)
            pygame.draw.polygon(screen, color, wing_bottom)
            pygame.draw.polygon(screen, outline, nose, max(1, int(2 * zoom)))
            pygame.draw.polygon(screen, outline, wing_top, max(1, int(2 * zoom)))
            pygame.draw.polygon(screen, outline, wing_bottom, max(1, int(2 * zoom)))
            pygame.draw.circle(screen, flash, (x + scaled, y), max(2, int(3 * zoom)))
        else:
            # round body with cross arms
            pygame.draw.circle(screen, color, (x, y), scaled)
            pygame.draw.circle(screen, outline, (x, y), scaled, max(1, int(2 * zoom)))
            horiz = pygame.Rect(x - scaled // 2, y - scaled // 8, scaled, scaled // 4)
            vert = pygame.Rect(x - scaled // 8, y - scaled // 2, scaled // 4, scaled)
            pygame.draw.rect(screen, color, horiz)
            pygame.draw.rect(screen, color, vert)
            pygame.draw.rect(screen, outline, horiz, max(1, int(2 * zoom)))
            pygame.draw.rect(screen, outline, vert, max(1, int(2 * zoom)))
            pygame.draw.circle(screen, flash, (x, y), max(2, int(3 * zoom)))

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        """Return ``True`` if ``(x, y)`` overlaps this capital ship."""
        r = max(self.radius, self.aura_radius)
        return math.hypot(self.x - x, self.y - y) < r + radius


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


def spawn_capital_ships(
    fractions: list[Fraction], width: int, height: int
) -> list[CapitalShip]:
    """Return one capital ship per faction placed randomly in the world."""
    ships = []
    for frac in fractions:
        ship = CapitalShip(name=f"{frac.name} Flagship")
        ship.apply_fraction_traits(frac)
        ship.x = random.randint(0, width)
        ship.y = random.randint(0, height)
        ships.append(ship)
    return ships
