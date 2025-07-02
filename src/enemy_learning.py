import math
import random
import pickle
import os
from dataclasses import dataclass, field

from enemy import Enemy, Flee, Defend, Attack, Pursue, Idle, _NullKeys
import config


Q_TABLE_PATH = "learning_enemy_q_table.pkl"


@dataclass
class LearningEnemy(Enemy):
    """Enemy with a simple Q-learning algorithm."""

    alpha: float = 0.5
    gamma: float = 0.9
    epsilon: float = 0.1
    q_table: dict = field(default_factory=dict, init=False, repr=False)
    prev_hull: int = field(default=0, init=False, repr=False)
    player_prev_hull: int = field(default=0, init=False, repr=False)

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
        """Return a discrete state representation."""
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
        return dist_cat, hull_low

    def choose_action(self, state: tuple) -> str:
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(list(self.actions))
        return max(self.q_table[state], key=self.q_table[state].get)

    def save_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Persist the Q-table to disk."""
        with open(path, "wb") as f:
            pickle.dump(self.q_table, f)

    def load_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Load Q-table values if a saved table exists."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.q_table = pickle.load(f)

    def learn(self, state: tuple, action: str, reward: float, next_state: tuple) -> None:
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
    ) -> None:
        self.player_ship = player_ship
        if not self.prev_hull:
            self.prev_hull = self.ship.hull
        if not self.player_prev_hull:
            self.player_prev_hull = player_ship.hull
        state = self._state()
        action = self.choose_action(state)
        self.perform_action(action)
        self.ship.update(_NullKeys(), dt, world_width, world_height, sectors, blackholes)
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
    from sector import Sector
    from character import Alien, Human, Robot

    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    model = random.choice(SHIP_MODELS)
    x = random.randint(region.x, region.x + region.width)
    y = random.randint(region.y, region.y + region.height)
    enemy = LearningEnemy(Ship(x, y, model), species, region)
    enemy.load_q_table()
    # Set the weapon cooldown using the configured value
    if enemy.ship.weapons:
        enemy.ship.weapons[0].cooldown = config.ENEMY_WEAPON_COOLDOWN
    return enemy
