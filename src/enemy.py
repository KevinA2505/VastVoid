import math
import random
from dataclasses import dataclass, field

import pygame

from character import Alien, Human, Robot
from ship import Ship, SHIP_MODELS
from sector import Sector


class _NullKeys:
    """Object that returns ``False`` for any key lookup."""

    def __getitem__(self, key):
        return False


class _Point:
    """Simple point container used for autopilot targets."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


@dataclass
class Enemy:
    """Autonomous ship pilot able to attack, defend and flee."""

    ship: Ship
    species: object
    region: Sector
    attack_range: float = 350.0
    detection_range: float = 800.0
    flee_threshold: int = 30
    state: str = field(default="idle", init=False)
    _flee_target: _Point | None = field(default=None, init=False, repr=False)
    _wander_target: _Point | None = field(default=None, init=False, repr=False)

    def update(
        self,
        player_ship: Ship,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
    ) -> None:
        """Update enemy behaviour and ship movement."""
        dx = player_ship.x - self.ship.x
        dy = player_ship.y - self.ship.y
        dist = math.hypot(dx, dy)

        in_region = (
            self.region.x <= player_ship.x <= self.region.x + self.region.width
            and self.region.y <= player_ship.y <= self.region.y + self.region.height
        )

        if self.ship.hull <= self.flee_threshold:
            self.state = "flee"
        elif in_region and dist <= self.attack_range:
            self.state = "attack"
        elif in_region and dist <= self.detection_range:
            self.state = "pursue"
        else:
            self.state = "idle"

        if self.state == "attack":
            angle = math.atan2(dy, dx)
            dest_x = player_ship.x - math.cos(angle) * 120
            dest_y = player_ship.y - math.sin(angle) * 120
            self.ship.start_autopilot(_Point(dest_x, dest_y))
            self.ship.fire(player_ship.x, player_ship.y)
        elif self.state == "pursue":
            self.ship.start_autopilot(player_ship)
        elif self.state == "flee":
            if self._flee_target is None or self.ship.autopilot_target is None:
                angle = math.atan2(-dy, -dx)
                dest_x = self.ship.x + math.cos(angle) * self.detection_range
                dest_y = self.ship.y + math.sin(angle) * self.detection_range
                self._flee_target = _Point(dest_x, dest_y)
                self.ship.start_autopilot(self._flee_target)
        else:
            if self.ship.autopilot_target is None:
                if self._wander_target is None:
                    wx = random.randint(self.region.x, self.region.x + self.region.width)
                    wy = random.randint(self.region.y, self.region.y + self.region.height)
                    self._wander_target = _Point(wx, wy)
                self.ship.start_autopilot(self._wander_target)

        self.ship.update(_NullKeys(), dt, world_width, world_height, sectors, blackholes)

        if self.state == "idle" and self.ship.autopilot_target is None:
            self._wander_target = None


def create_random_enemy(region: Sector) -> Enemy:
    """Return an enemy with random species and ship model inside a region."""
    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    model = random.choice(SHIP_MODELS)
    x = random.randint(region.x, region.x + region.width)
    y = random.randint(region.y, region.y + region.height)
    return Enemy(Ship(x, y, model), species, region)
