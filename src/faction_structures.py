# New faction-aware generic structures

import random
import math
from dataclasses import dataclass, field
from typing import Any
from star import Star
from combat import Drone
from defensive_drone import DefensiveDrone
from learning_defensive_drone import LearningDefensiveDrone
from aggressive_defensive_drone import AggressiveDefensiveDrone
from station import SpaceStation
import pygame
import config


@dataclass
class CityBuilding:
    """Simple decorative building used for Cosmic Guild cities."""

    x: float
    y: float
    shape: str
    size: int = 20

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        scaled = int(self.size * zoom)
        fill = (0, 0, 0)
        outline = (255, 215, 0)
        if self.shape == "circle":
            pygame.draw.circle(screen, fill, (cx, cy), scaled)
            pygame.draw.circle(screen, outline, (cx, cy), scaled, max(1, int(2 * zoom)))
        elif self.shape == "square":
            rect = pygame.Rect(cx - scaled, cy - scaled, scaled * 2, scaled * 2)
            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, outline, rect, max(1, int(2 * zoom)))
        elif self.shape == "triangle":
            points = [
                (cx + scaled * math.cos(a), cy + scaled * math.sin(a))
                for a in [math.radians(-90), math.radians(30), math.radians(150)]
            ]
            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, outline, points, max(1, int(2 * zoom)))
        elif self.shape == "pentagon":
            points = [
                (
                    cx + scaled * math.cos(i * 2 * math.pi / 5 - math.pi / 2),
                    cy + scaled * math.sin(i * 2 * math.pi / 5 - math.pi / 2),
                )
                for i in range(5)
            ]
            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, outline, points, max(1, int(2 * zoom)))

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        return math.hypot(self.x - x, self.y - y) < self.size + radius

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
class EngagementRing:
    """Golden ring surrounding the Nebula Order flagship."""

    owner: "CapitalShip"
    radius: float
    thickness: float = 20.0
    color: Color = (255, 215, 0)

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        cx = int((self.owner.x - offset_x) * zoom)
        cy = int((self.owner.y - offset_y) * zoom)
        pygame.draw.circle(
            screen,
            self.color,
            (cx, cy),
            int(self.radius * zoom),
            max(1, int(self.thickness * zoom)),
        )
        outline_w = max(1, int(2 * zoom))
        pygame.draw.circle(
            screen,
            (0, 0, 0),
            (cx, cy),
            int(self.radius * zoom),
            outline_w,
        )
        inner_r = int(max(0, (self.radius - self.thickness)) * zoom)
        if inner_r > 0:
            pygame.draw.circle(
                screen,
                (0, 0, 0),
                (cx, cy),
                inner_r,
                outline_w,
            )

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        dist = math.hypot(self.owner.x - x, self.owner.y - y)
        inner = max(0.0, self.radius - self.thickness)
        return inner - radius < dist < self.radius + radius


@dataclass
class CapitalShip(FactionStructure):
    """Large mobile base acting as the heart of a faction."""

    x: float = 0.0
    y: float = 0.0
    hull: int = 1000
    hangar_capacity: int = 4
    energy: float = 0.0
    max_energy: float = 10000.0
    energy_sources: list[Any] = field(default_factory=list)
    # Basic collision/scale size used by drones and other systems
    size: int = 50
    radius: int = 50
    aura_radius: int = 80
    arms: list[ChannelArm] = field(default_factory=list)
    drones: list[Drone] = field(default_factory=list)
    engagement_ring: EngagementRing | None = None
    city_stations: list[Any] = field(default_factory=list)

    def apply_fraction_traits(self, fraction: Fraction) -> None:
        super().apply_fraction_traits(fraction)
        # Default size is tied to the collision radius so dependent systems
        # like drones have a sensible orbit distance.
        self.size = self.radius
        if fraction.name == "Solar Dominion":
            self.hull = 1500
            self.modules.extend(["Heavy Cannons", "Fighter Bays"])
            self.aura_radius = 240
            self.radius = max(self.radius, self.aura_radius)
            # Update size after modifying the radius
            self.size = self.radius
            # Solar Dominion ships start fully charged
            self.energy = self.max_energy
            self.arms = [
                ChannelArm(i * 2 * math.pi / 5, self.radius)
                for i in range(5)
            ]
        elif fraction.name == "Cosmic Guild":
            self.hull = 1200
            self.modules.extend(["Trade Hub", "Drone Bays"])
            self.city_stations = []

            shapes = (
                ["square"] * 4
                + ["circle"] * 3
                + ["pentagon"]
                + ["triangle"] * 2
            )
            distance = self.radius * 5
            placed: list[CityBuilding] = []
            for shape in shapes:
                for _ in range(20):
                    ang = random.uniform(0, 2 * math.pi)
                    dist = random.uniform(distance * 0.8, distance * 1.2)
                    sx = self.x + math.cos(ang) * dist
                    sy = self.y + math.sin(ang) * dist
                    b = CityBuilding(sx, sy, shape)
                    if math.hypot(sx - self.x, sy - self.y) < self.radius + b.size:
                        continue
                    if any(
                        math.hypot(sx - o.x, sy - o.y) < b.size + o.size
                        for o in placed
                    ):
                        continue
                    placed.append(b)
                    self.city_stations.append(b)
                    break
        elif fraction.name == "Nebula Order":
            self.hull = 1100
            self.modules.extend(["Research Labs", "Sensor Array"])
            self.size = self.radius
            self.engagement_ring = EngagementRing(
                self,
                self.size * 5,
                thickness=self.size * 0.6,
            )
            self.drones = []
            ring_radius = self.engagement_ring.radius * 1.15
            for i in range(10):
                drone = AggressiveDefensiveDrone(
                    self,
                    ring_radius,
                    orbit_speed=-0.75,
                    speed_factor=config.NPC_SPEED_FACTOR,
                )
                drone.angle = i * 2 * math.pi / 10
                self.drones.append(drone)
        elif fraction.name == "Pirate Clans":
            self.hull = 1000
            self.modules.extend(["Cloaking Device", "Raider Hangars"])
        elif fraction.name == "Free Explorers":
            self.hull = 1300
            self.modules.extend(["Survey Deck", "Jump Drives"])

    def update(
        self,
        dt: float,
        sectors: list,
        targets: list | None = None,
        player: object | None = None,
    ) -> None:
        if not self.fraction:
            return
        if targets is None:
            targets = []
        if self.fraction.name == "Solar Dominion":
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
                    # Recharge energy from the linked star
                    if self.energy < self.max_energy:
                        # Each channel arm can move up to 10 energy units per
                        # second from its linked star, limited by the star's
                        # remaining energy and the ship's current deficit.
                        transfer = 10.0 * dt
                        available = min(transfer, arm.target.energy)
                        needed = self.max_energy - self.energy
                        amount = min(available, needed)
                        self.energy += amount
                        arm.target.energy -= amount
        elif self.fraction.name == "Nebula Order":
            hostiles = [e for e in targets if e.fraction != self.fraction]
            if player and getattr(player, "fraction", None) != self.fraction:
                hostiles.append(type("_P", (), {"ship": player})())
            for drone in list(self.drones):
                drone.update(dt, hostiles)

                rect = pygame.Rect(
                    drone.x - drone.size / 2,
                    drone.y - drone.size / 2,
                    drone.size,
                    drone.size,
                )

                for en in hostiles:
                    for proj in list(en.ship.projectiles):
                        if rect.collidepoint(proj.x, proj.y):
                            drone.hp -= proj.damage
                            en.ship.projectiles.remove(proj)

                for proj in list(drone.projectiles):
                    for en in hostiles:
                        if (
                            math.hypot(proj.x - en.ship.x, proj.y - en.ship.y)
                            <= en.ship.collision_radius
                        ):
                            en.ship.take_damage(proj.damage)
                            drone.projectiles.remove(proj)
                            break

                for en in hostiles:
                    if math.hypot(en.ship.x - drone.x, en.ship.y - drone.y) <= en.ship.collision_radius + drone.size / 2:
                        drone.hp -= 5
                        en.ship.take_damage(5)

                if drone.expired():
                    self.drones.remove(drone)

        for station in self.city_stations:
            if hasattr(station, "update"):
                station.update(dt)

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
        for station in self.city_stations:
            station.draw(screen, offset_x, offset_y, zoom)
        if self.engagement_ring:
            self.engagement_ring.draw(screen, offset_x, offset_y, zoom)
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
                pygame.draw.circle(
                    screen,
                    flash,
                    (lx, ly),
                    max(2, int(3 * zoom))
                )
        elif self.fraction and self.fraction.name == "Cosmic Guild":
            dark_blue = (10, 10, 80)
            gold = (255, 215, 0)
            square = pygame.Rect(x - scaled // 2, y - scaled // 2, scaled, scaled)
            pygame.draw.rect(screen, dark_blue, square)
            pygame.draw.rect(screen, gold, square, max(1, int(4 * zoom)))
            font_size = max(10, int(scaled * 0.7))
            font = pygame.font.Font(None, font_size)
            letter = font.render("C", True, (0, 0, 0))
            letter_rect = letter.get_rect(center=(x, y))
            screen.blit(letter, letter_rect)
            aura_r = int(self.aura_radius * zoom)
            if aura_r > 0:
                aura = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(aura, (0, 0, 0, int(255 * 0.8)), (aura_r, aura_r), aura_r)
                screen.blit(aura, (x - aura_r, y - aura_r))
        elif self.fraction and self.fraction.name == "Nebula Order":
            outer_r = scaled
            mid_r = int(scaled * 0.65)
            inner_r = int(scaled * 0.3)
            dark_purple = (60, 20, 90)
            mid_purple = (110, 50, 150)
            light_purple = (160, 100, 210)

            pygame.draw.circle(screen, dark_purple, (x, y), outer_r)
            pygame.draw.circle(screen, mid_purple, (x, y), mid_r)
            dot_r = max(2, int(scaled * 0.08))
            for dx, dy in [
                (0, -mid_r),
                (0, mid_r),
                (-mid_r, 0),
                (mid_r, 0),
            ]:
                pygame.draw.circle(screen, (0, 0, 0), (x + dx, y + dy), dot_r)
            pygame.draw.circle(screen, light_purple, (x, y), inner_r)
            for drone in self.drones:
                drone.draw(screen, offset_x, offset_y, zoom)
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
        """Return ``True`` if ``(x, y)`` overlaps this capital ship or its ring."""
        r = max(self.radius, self.aura_radius)
        if self.fraction and self.fraction.name == "Cosmic Guild":
            if (
                self.x - r - radius < x < self.x + r + radius
                and self.y - r - radius < y < self.y + r + radius
            ):
                return True
        else:
            if math.hypot(self.x - x, self.y - y) < r + radius:
                return True
        if self.engagement_ring and self.engagement_ring.collides_with_point(x, y, radius):
            return True
        for station in self.city_stations:
            if hasattr(station, "collides_with_point"):
                if station.collides_with_point(x, y, radius):
                    return True
            elif math.hypot(station.x - x, station.y - y) < getattr(station, "radius", 0) + radius:
                return True
        return False


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
    """Beacon marking territory and granting nearby bonuses."""

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
        ship.x = random.randint(0, width)
        ship.y = random.randint(0, height)
        ship.apply_fraction_traits(frac)
        ships.append(ship)
    return ships
