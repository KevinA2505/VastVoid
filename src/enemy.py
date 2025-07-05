import math
import random
from dataclasses import dataclass, field
from typing import List
from fraction import Fraction, FRACTIONS

import py_trees

from character import Alien, Human, Robot
from ship import Ship, SHIP_MODELS
from artifact import (
    Artifact,
    Decoy,
    EMPArtifact,
    AreaShieldArtifact,
    GravityTractorArtifact,
    NanobotArtifact,
    SolarGeneratorArtifact,
    DecoyArtifact,
    AVAILABLE_ARTIFACTS,
)
from combat import (
    LaserWeapon,
    MineWeapon,
    DroneWeapon,
    MissileWeapon,
    BasicWeapon,
)
from sector import Sector
import config


class _NullKeys:
    """Object that returns ``False`` for any key lookup."""

    def __getitem__(self, key):
        return False


class _Point:
    """Simple point container used for autopilot targets."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class EnemyManager:
    """Global manager keeping track of active enemies and coordination requests."""

    def __init__(self) -> None:
        self.enemies: List["Enemy"] = []

    def register(self, enemy: "Enemy") -> None:
        if enemy not in self.enemies:
            self.enemies.append(enemy)

    def unregister(self, enemy: "Enemy") -> None:
        if enemy in self.enemies:
            self.enemies.remove(enemy)

    def request_help(self, caller: "Enemy", target: object) -> None:
        """Notify allies to assist ``caller`` against ``target``."""
        for ally in self.enemies:
            if ally is caller:
                continue
            if ally.fraction == caller.fraction:
                ally.assist_target = target
        self.assign_orbit_sides(caller.fraction, target)

    def assign_orbit_sides(self, fraction: Fraction, target: object) -> None:
        allies = [
            e
            for e in self.enemies
            if (e.target is target or e.assist_target is target)
            and e.fraction == fraction
            and e.ship.hull > 0
        ]
        for i, ally in enumerate(sorted(allies, key=id)):
            ally.orbit_side = 1 if i % 2 == 0 else -1


enemy_manager = EnemyManager()


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
        target = enemy.target
        dx = target.x - ship.x
        dy = target.y - ship.y
        if ship.hull > enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "flee"
        if enemy._flee_target is None or ship.autopilot_target is None:
            angle = math.atan2(-dy, -dx)
            dest_x = ship.x + math.cos(angle) * enemy.detection_range
            dest_y = ship.y + math.sin(angle) * enemy.detection_range
            enemy._flee_target = _Point(dest_x, dest_y)
            ship.start_autopilot(enemy._flee_target)
            if ship.boost_charge >= 1.0:
                ship.boost_time = config.BOOST_DURATION
                ship.boost_charge = 0.0
        return py_trees.common.Status.SUCCESS


class Attack(_EnemyBehaviour):
    def __init__(self, enemy: "Enemy") -> None:
        super().__init__("Attack", enemy)

    def update(self) -> py_trees.common.Status:
        enemy = self.enemy
        ship = enemy.ship
        target = enemy.target
        dx = target.x - ship.x
        dy = target.y - ship.y
        dist = math.hypot(dx, dy)
        in_region = (
            enemy.region.x <= target.x <= enemy.region.x + enemy.region.width
            and enemy.region.y <= target.y <= enemy.region.y + enemy.region.height
        )
        if not (in_region and dist <= enemy.attack_range) or ship.hull <= enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "attack"
        # If close enough, orbit the player instead of moving directly towards
        # them. This uses the same orbit parameters available to the player.
        if ship.orbit_time <= 0 and dist <= enemy.attack_range:
            if enemy.orbit_timer <= 0:
                enemy.orbit_timer = config.ENEMY_ORBIT_INTERVAL
                if random.random() < config.ENEMY_ORBIT_PROBABILITY:
                    ship.start_orbit(
                        target,
                        speed=config.SHIP_ORBIT_SPEED * 0.5 * enemy.orbit_side,
                    )
        if ship.orbit_time <= 0:
            angle = math.atan2(dy, dx)
            dest_x = target.x - math.cos(angle) * 120
            dest_y = target.y - math.sin(angle) * 120
            ship.start_autopilot(_Point(dest_x, dest_y))
        ship.fire(target.x, target.y)
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
        target = enemy.target
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
            dx = target.x - ship.x
            dy = target.y - ship.y
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
        target = enemy.target
        dx = target.x - ship.x
        dy = target.y - ship.y
        dist = math.hypot(dx, dy)
        in_region = (
            enemy.region.x <= target.x <= enemy.region.x + enemy.region.width
            and enemy.region.y <= target.y <= enemy.region.y + enemy.region.height
        )
        if not (in_region and dist <= enemy.detection_range) or ship.hull <= enemy.flee_threshold:
            return py_trees.common.Status.FAILURE
        enemy.state = "pursue"
        ship.start_autopilot(target)
        if ship.boost_charge >= 1.0:
            ship.boost_time = config.BOOST_DURATION
            ship.boost_charge = 0.0
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
    fraction: Fraction
    attack_range: float = 385.0
    detection_range: float = 800.0
    flee_threshold: int = 30
    state: str = field(default="idle", init=False)
    _flee_target: _Point | None = field(default=None, init=False, repr=False)
    _wander_target: _Point | None = field(default=None, init=False, repr=False)
    player_ship: Ship | None = field(default=None, init=False, repr=False)
    target: object | None = field(default=None, init=False, repr=False)
    assist_target: object | None = field(default=None, init=False, repr=False)
    orbit_side: int = field(default=1, init=False)
    tree: py_trees.trees.BehaviourTree | None = field(default=None, init=False, repr=False)
    orbit_timer: float = field(
        default=config.ENEMY_ORBIT_INTERVAL,
        init=False,
        repr=False,
    )
    artifacts: list[Artifact] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.build_tree()
        self.ship.artifacts = self.artifacts
        enemy_manager.register(self)

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

    def _maybe_use_artifacts(self, player_ship: Ship, dist_to_player: float) -> None:
        """Randomly activate equipped artifacts based on the situation."""
        for idx, art in enumerate(self.ship.artifacts):
            if isinstance(art, EMPArtifact):
                if dist_to_player <= art.radius and random.random() < 0.2:
                    self.ship.use_artifact(idx, [player_ship])
            elif isinstance(art, AreaShieldArtifact):
                if self.ship.area_shield is None and random.random() < 0.05:
                    self.ship.use_artifact(idx, [player_ship])
            elif isinstance(art, NanobotArtifact):
                if (
                    self.ship.hull < self.ship.max_hull * 0.6
                    and random.random() < 0.05
                ):
                    self.ship.use_artifact(idx, [player_ship])
            elif isinstance(art, DecoyArtifact):
                if self.state in {"flee", "defend"} and random.random() < 0.1:
                    self.ship.use_artifact(idx, [player_ship])
            elif isinstance(art, GravityTractorArtifact):
                if random.random() < 0.05 and not art.awaiting_click:
                    art.activate(self.ship, [player_ship])
                    if art.awaiting_click:
                        art.confirm(player_ship.x, player_ship.y)
            elif isinstance(art, SolarGeneratorArtifact):
                if random.random() < 0.05:
                    self.ship.use_artifact(idx, [player_ship])

    def update(
        self,
        player_ship: Ship,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
        player_fraction: Fraction | None = None,
    ) -> None:
        """Update ship movement after behaviour tree tick."""

        self.player_ship = player_ship
        dist_to_player = math.hypot(
            player_ship.x - self.ship.x, player_ship.y - self.ship.y
        )
        if (
            dist_to_player <= self.detection_range
            or self.ship.hull <= self.flee_threshold
        ):
            enemy_manager.request_help(self, player_ship)
        if player_fraction is not None and player_fraction == self.fraction:
            self.state = "ally"
            self.ship.update(
                _NullKeys(), dt, world_width, world_height, sectors, blackholes, None
            )
            if self.ship.autopilot_target is None:
                self._wander_target = None
            return
        if self.assist_target is not None:
            self.target = self.assist_target
        else:
            self.target = player_ship
            for obj in getattr(player_ship, "specials", []):
                if isinstance(obj, Decoy) and not obj.expired():
                    self.target = obj
                    break
        if isinstance(self.ship.orbit_target, Decoy) and self.ship.orbit_target.expired():
            self.ship.cancel_orbit()
        self.orbit_timer = max(0.0, self.orbit_timer - dt)
        if self.tree:
            self.tree.tick()

        self._maybe_use_artifacts(player_ship, dist_to_player)

        self.ship.update(
            _NullKeys(), dt, world_width, world_height, sectors, blackholes, None
        )

        # Break orbit if the player is boosting so the enemy can't keep up
        if (
            player_ship.boost_time > 0
            and self.ship.orbit_target is player_ship
            and self.ship.orbit_time > 0
        ):
            self.ship.cancel_orbit()

        if self.state == "idle" and self.ship.autopilot_target is None:
            self._wander_target = None


def create_random_enemy(region: Sector) -> Enemy:
    """Return an enemy with random species and ship model inside a region."""
    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    model = random.choice(SHIP_MODELS)
    x = random.randint(region.x, region.x + region.width)
    y = random.randint(region.y, region.y + region.height)
    fraction = random.choice(FRACTIONS)
    enemy = Enemy(
        Ship(x, y, model, hull=config.ENEMY_MAX_HULL),
        species,
        region,
        fraction,
    )
    num_artifacts = random.randint(1, 2)
    art_classes = random.sample(AVAILABLE_ARTIFACTS, num_artifacts)
    enemy.artifacts = [cls() for cls in art_classes]
    enemy.ship.artifacts = enemy.artifacts
    # Replace the default weapon with a random one
    weapon_cls = random.choice(
        [LaserWeapon, MineWeapon, DroneWeapon, MissileWeapon, BasicWeapon]
    )
    enemy.ship.weapons = [weapon_cls()]
    for w in enemy.ship.weapons:
        w.owner = enemy.ship
        # Use a configurable cooldown so enemies don't spam shots
        w.cooldown = config.ENEMY_WEAPON_COOLDOWN
    enemy_manager.register(enemy)
    return enemy
