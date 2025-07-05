import math
import random
import pickle
import os
from dataclasses import dataclass, field

from enemy import Enemy, Flee, Defend, Attack, Pursue, Idle, _NullKeys, enemy_manager
from fraction import FRACTIONS
from artifact import Decoy
from combat import (
    LaserWeapon,
    MineWeapon,
    DroneWeapon,
    MissileWeapon,
    BasicWeapon,
)
import config


Q_TABLE_PATH = "learning_enemy_q_table.pkl"
Q_TABLE_VERSION = 2


@dataclass
class LearningEnemy(Enemy):
    """Enemy with a simple Q-learning algorithm."""

    alpha: float = 0.5
    gamma: float = 0.9
    epsilon: float = 0.1
    q_table: dict = field(default_factory=dict, init=False, repr=False)
    q_table_version: int = field(default=Q_TABLE_VERSION, init=False, repr=False)
    prev_hull: int = field(default=0, init=False, repr=False)
    player_prev_hull: int = field(default=0, init=False, repr=False)
    _blackholes: list | None = field(default=None, init=False, repr=False)

    def build_tree(self) -> None:  # override without behaviour tree
        self.actions = {
            "flee": Flee(self),
            "defend": Defend(self),
            "attack": Attack(self),
            "pursue": Pursue(self),
            "idle": Idle(self),
        }
        self.tree = None

    def _state(self) -> tuple:
        """Return a discrete state representation.

        The state now includes additional features describing shield strength
        and proximity to hazards so the Q-table can learn richer behaviours.
        """
        player = self.player_ship
        dx = player.x - self.ship.x
        dy = player.y - self.ship.y
        dist = math.hypot(dx, dy)

        if dist <= self.attack_range:
            dist_cat = 0
        elif dist <= self.detection_range:
            dist_cat = 1
        else:
            dist_cat = 2

        hull_low = self.ship.hull <= self.flee_threshold

        def shield_cat(shield) -> int:
            ratio = shield.strength / shield.max_strength
            if ratio > 0.66:
                return 2
            if ratio > 0.33:
                return 1
            return 0

        enemy_shield = shield_cat(self.ship.shield)
        player_shield = shield_cat(player.shield)

        near_blackhole = 0
        if getattr(self, "_blackholes", None):
            for hole in self._blackholes:
                d = math.hypot(self.ship.x - hole.x, self.ship.y - hole.y)
                if d <= hole.pull_range:
                    near_blackhole = 1
                    break

        return dist_cat, hull_low, enemy_shield, player_shield, near_blackhole

    def choose_action(self, state: tuple) -> str:
        """Return an action for ``state`` using an epsilon-greedy policy."""
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(list(self.actions))
        return max(self.q_table[state], key=self.q_table[state].get)

    def save_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Persist the Q-table to disk."""
        with open(path, "wb") as f:
            data = {"version": self.q_table_version, "q_table": self.q_table}
            pickle.dump(data, f)

    def load_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Load Q-table values if a saved table exists."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
            if isinstance(data, dict) and "version" in data:
                version = data.get("version", 1)
                table = data.get("q_table", {})
            else:
                version = 1
                table = data

            if version == 1:
                new_table = {}
                for state, actions in table.items():
                    if isinstance(state, tuple) and len(state) == 2:
                        new_state = state + (1, 1, 0)
                    else:
                        new_state = state
                    new_table[new_state] = actions
                self.q_table = new_table
                self.q_table_version = Q_TABLE_VERSION
            else:
                self.q_table = table
                self.q_table_version = version

    def learn(self, state: tuple, action: str, reward: float, next_state: tuple) -> None:
        """Update Q-values based on the transition from ``state`` to ``next_state``."""
        q_state = self.q_table.setdefault(state, {a: 0.0 for a in self.actions})
        q_next = self.q_table.setdefault(next_state, {a: 0.0 for a in self.actions})
        q_state[action] += self.alpha * (
            reward + self.gamma * max(q_next.values()) - q_state[action]
        )

    def compute_reward(self) -> float:
        reward = 0.0
        if self.player_prev_hull:
            reward += self.player_prev_hull - self.player_ship.hull
        if self.prev_hull:
            reward -= self.prev_hull - self.ship.hull
        dx = self.player_ship.x - self.ship.x
        dy = self.player_ship.y - self.ship.y
        if math.hypot(dx, dy) <= self.attack_range:
            reward += 0.1
        return reward

    def perform_action(self, action: str) -> None:
        behaviour = self.actions[action]
        behaviour.update()

    def update(
        self,
        player_ship,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
        player_fraction=None,
    ) -> None:
        self.player_ship = player_ship
        self._blackholes = blackholes
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
            self.ship.update(_NullKeys(), dt, world_width, world_height, sectors, blackholes, None)
            if self.ship.autopilot_target is None:
                self._wander_target = None
            self.prev_hull = self.ship.hull
            self.player_prev_hull = player_ship.hull
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
        if not self.prev_hull:
            self.prev_hull = self.ship.hull
        if not self.player_prev_hull:
            self.player_prev_hull = player_ship.hull
        state = self._state()
        action = self.choose_action(state)
        self.perform_action(action)
        self.ship.update(_NullKeys(), dt, world_width, world_height, sectors, blackholes, None)

        if (
            player_ship.boost_time > 0
            and self.ship.orbit_target is player_ship
            and self.ship.orbit_time > 0
        ):
            self.ship.cancel_orbit()
        reward = self.compute_reward()
        next_state = self._state()
        self.learn(state, action, reward, next_state)
        if self.state == "idle" and self.ship.autopilot_target is None:
            self._wander_target = None
        self.prev_hull = self.ship.hull
        self.player_prev_hull = player_ship.hull


def create_learning_enemy(region):
    """Return a LearningEnemy with random species and ship model."""
    from ship import Ship, SHIP_MODELS
    from character import Alien, Human, Robot

    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    model = random.choice(SHIP_MODELS)
    x = random.randint(region.x, region.x + region.width)
    y = random.randint(region.y, region.y + region.height)
    fraction = random.choice(FRACTIONS)
    enemy = LearningEnemy(
        Ship(x, y, model, hull=config.ENEMY_MAX_HULL),
        species,
        region,
        fraction,
    )
    enemy.load_q_table()
    # Replace the default weapon with a random one
    weapon_cls = random.choice(
        [LaserWeapon, MineWeapon, DroneWeapon, MissileWeapon, BasicWeapon]
    )
    enemy.ship.weapons = [weapon_cls()]
    for w in enemy.ship.weapons:
        w.owner = enemy.ship
        # Set the weapon cooldown using the configured value
        w.cooldown = config.ENEMY_WEAPON_COOLDOWN
    enemy_manager.register(enemy)
    return enemy
