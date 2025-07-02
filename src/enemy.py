import math
import random
from dataclasses import dataclass, field

import py_trees

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


class _EnemyBehaviour(py_trees.behaviour.Behaviour):
    """Base behaviour storing a reference to the enemy instance."""

    def __init__(self, name: str, enemy: "Enemy") -> None:
        super().__init__(name)
        self.enemy = enemy


class Flee(_EnemyBehaviour):
    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Flee", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        player = enemy.player_ship
        dx = player.x - ship.x
        dy = player.y - ship.y
        if ship.hull > enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "flee"
        if enemy._flee_target is None or ship.autopilot_target is None:
            angle = math.atan2(-dy, -dx)
            dest_x = ship.x + math.cos(angle) * enemy.detection_range
            dest_y = ship.y + math.sin(angle) * enemy.detection_range
            enemy._flee_target = _Point(dest_x, dest_y)
            ship.start_autopilot(enemy._flee_target)
        return py_trees.common.Status.SUCCESS


class Attack(_EnemyBehaviour):
    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Attack", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        player = enemy.player_ship
        dx = player.x - ship.x
        dy = player.y - ship.y
        dist = math.hypot(dx, dy)
        in_region = (
            enemy.region.x <= player.x <= enemy.region.x + enemy.region.width
            and enemy.region.y <= player.y <= enemy.region.y + enemy.region.height
        )
        if not (in_region and dist <= enemy.attack_range) or ship.hull <= enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "attack"
        angle = math.atan2(dy, dx)
        dest_x = player.x - math.cos(angle) * 120
        dest_y = player.y - math.sin(angle) * 120
        ship.start_autopilot(_Point(dest_x, dest_y))
        ship.fire(player.x, player.y)
        return py_trees.common.Status.SUCCESS


class Defend(_EnemyBehaviour):
    """Evasive manoeuvres when shields are low or projectiles are near."""

    DANGER_RANGE = 200
    SHIELD_THRESHOLD = 0.3

    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Defend", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        player = enemy.player_ship
        if not player:
            return py_trees.common.Status.FAILURE

        shield_ratio = ship.shield.strength / ship.shield.max_strength
        near_proj = any(
            math.hypot(proj.x - ship.x, proj.y - ship.y) <= self.DANGER_RANGE
            for proj in player.projectiles
        )

        if shield_ratio < self.SHIELD_THRESHOLD or near_proj:
            enemy.state = "defend"
            dx = player.x - ship.x
            dy = player.y - ship.y
            angle = math.atan2(dy, dx) + math.pi / 2
            dist = enemy.detection_range / 2
            dest_x = ship.x + math.cos(angle) * dist
            dest_y = ship.y + math.sin(angle) * dist
            ship.start_autopilot(_Point(dest_x, dest_y))
            return py_trees.common.Status.SUCCESS

        return py_trees.common.Status.FAILURE


class Pursue(_EnemyBehaviour):
    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Pursue", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        player = enemy.player_ship
        dx = player.x - ship.x
        dy = player.y - ship.y
        dist = math.hypot(dx, dy)
        in_region = (
            enemy.region.x <= player.x <= enemy.region.x + enemy.region.width
            and enemy.region.y <= player.y <= enemy.region.y + enemy.region.height
        )
        if not (in_region and dist <= enemy.detection_range) or ship.hull <= enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "pursue"
        ship.start_autopilot(player)
        return py_trees.common.Status.SUCCESS


class Idle(_EnemyBehaviour):
    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Idle", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        enemy.state = "idle"
        if ship.autopilot_target is None:
            if enemy._wander_target is None:
                wx = random.randint(enemy.region.x, enemy.region.x + enemy.region.width)
                wy = random.randint(enemy.region.y, enemy.region.y + enemy.region.height)
                enemy._wander_target = _Point(wx, wy)
            ship.start_autopilot(enemy._wander_target)
        return py_trees.common.Status.SUCCESS


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
    player_ship: Ship | None = field(default=None, init=False, repr=False)
    tree: py_trees.trees.BehaviourTree | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.build_tree()

    def build_tree(self) -> None:
        """Create the behaviour tree controlling this enemy."""
        flee = Flee(self)
        defend = Defend(self)
        attack = Attack(self)
        pursue = Pursue(self)
        idle = Idle(self)
        root = py_trees.composites.Selector("EnemyRoot", memory=False)
        root.add_children([flee, defend, attack, pursue, idle])
        self.tree = py_trees.trees.BehaviourTree(root)

    def update(
        self,
        player_ship: Ship,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
    ) -> None:
        """Update ship movement after behaviour tree tick."""
        
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
