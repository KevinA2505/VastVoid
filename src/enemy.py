import math
import random
from dataclasses import dataclass, field

import pygame

from character import Alien, Human, Robot
from ship import Ship, SHIP_MODELS


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
    attack_range: float = 350.0
    detection_range: float = 800.0
    flee_threshold: int = 30
    state: str = field(default="idle", init=False)
    _flee_target: _Point | None = field(default=None, init=False, repr=False)

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

        if self.ship.hull <= self.flee_threshold:
            self.state = "flee"
        elif dist <= self.attack_range:
            self.state = "attack"
        elif dist <= self.detection_range:
            self.state = "pursue"
        else:
            self.state = "idle"

        if self.state == "attack":
            self.ship.start_autopilot(player_ship)
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
                self._flee_target = _Point(
                    random.randint(0, world_width),
                    random.randint(0, world_height),
                )
                self.ship.start_autopilot(self._flee_target)

        self.ship.update(_NullKeys(), dt, world_width, world_height, sectors, blackholes)


def create_random_enemy(x: int, y: int) -> Enemy:
    """Return an enemy with random species and ship model."""
    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    model = random.choice(SHIP_MODELS)
    return Enemy(Ship(x, y, model), species)
