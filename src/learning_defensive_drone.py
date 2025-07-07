import math
import random
import pickle
import os
from dataclasses import dataclass, field

from defensive_drone import DefensiveDrone
import config


Q_TABLE_PATH = "learning_defensive_drone_q_table.pkl"
Q_TABLE_VERSION = 1


def _dist(a_x: float, a_y: float, b_x: float, b_y: float) -> float:
    return math.hypot(a_x - b_x, a_y - b_y)


@dataclass
class LearningDefensiveDrone(DefensiveDrone):
    """Defensive drone with a very small Q-learning brain."""

    owner: object
    angle: float = 0.0
    orbit_radius: float | None = None
    orbit_speed: float = config.DEF_DRONE_ORBIT_SPEED
    hp: float = 20.0
    alpha: float = config.DEF_DRONE_ALPHA
    gamma: float = config.DEF_DRONE_GAMMA
    epsilon: float = config.DEF_DRONE_EPSILON
    patrol_radius: float = config.DEF_DRONE_PATROL_RADIUS
    detection_range: float = config.DEF_DRONE_DETECTION_RANGE
    q_table: dict = field(default_factory=dict, init=False, repr=False)
    q_table_version: int = field(default=Q_TABLE_VERSION, init=False, repr=False)
    prev_hp: float = field(default=0.0, init=False, repr=False)
    _wander_target: tuple | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        super().__init__(
            self.owner,
            self.angle,
            self.orbit_radius,
            self.orbit_speed,
            self.hp,
            speed_factor=config.NPC_SPEED_FACTOR,
        )

    def load_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Load the Q-table from disk if present."""
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
            if isinstance(data, dict) and "version" in data:
                version = data.get("version", 1)
                table = data.get("q_table", {})
            else:
                version = 1
                table = data
            self.q_table = table
            self.q_table_version = version

    def save_q_table(self, path: str = Q_TABLE_PATH) -> None:
        """Persist the Q-table so learning is retained."""
        with open(path, "wb") as f:
            data = {"version": self.q_table_version, "q_table": self.q_table}
            pickle.dump(data, f)

    # ------------------------------------------------------------------
    # Q-learning helpers
    # ------------------------------------------------------------------
    def _state(self, objects: list) -> tuple:
        """Return a simple discrete state description."""
        threat = self._find_threat(objects)
        if threat:
            d_threat = _dist(self.x, self.y, getattr(threat, "x", 0), getattr(threat, "y", 0))
            if d_threat <= self.detection_range * 0.5:
                threat_cat = 0
            elif d_threat <= self.detection_range:
                threat_cat = 1
            else:
                threat_cat = 2
        else:
            threat_cat = 3
        d_owner = _dist(self.x, self.y, self.owner.x, self.owner.y)
        if d_owner <= self.patrol_radius:
            owner_cat = 0
        elif d_owner <= self.patrol_radius * 2:
            owner_cat = 1
        else:
            owner_cat = 2
        hull_low = self.hp <= self.hp * 0.5
        return threat_cat, owner_cat, hull_low

    def choose_action(self, state: tuple) -> str:
        """Return an action for ``state`` using an epsilon-greedy policy."""
        actions = ["patrol", "intercept", "return"]
        if random.random() < self.epsilon or state not in self.q_table:
            return random.choice(actions)
        q_state = self.q_table[state]
        return max(q_state, key=q_state.get)

    def learn(self, state: tuple, action: str, reward: float, next_state: tuple) -> None:
        actions = ["patrol", "intercept", "return"]
        q_state = self.q_table.setdefault(state, {a: 0.0 for a in actions})
        q_next = self.q_table.setdefault(next_state, {a: 0.0 for a in actions})
        q_state[action] += self.alpha * (
            reward + self.gamma * max(q_next.values()) - q_state[action]
        )

    # ------------------------------------------------------------------
    # Behaviour helpers
    # ------------------------------------------------------------------
    def _move_towards(self, tx: float, ty: float, speed: float, dt: float) -> None:
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy) or 1.0
        self.x += (dx / dist * speed) * dt
        self.y += (dy / dist * speed) * dt

    def _patrol(self, dt: float) -> None:
        if self._wander_target is None or _dist(self.x, self.y, *self._wander_target) < 5:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(self.owner.size, self.patrol_radius)
            self._wander_target = (
                self.owner.x + math.cos(angle) * radius,
                self.owner.y + math.sin(angle) * radius,
            )
        self._move_towards(self._wander_target[0], self._wander_target[1], self.orbit_speed * 60, dt)

    def _intercept(self, dt: float, objects: list) -> None:
        if self.target is None or isinstance(self.target, object) and getattr(self.target, "expired", lambda: False)():
            self.target = self._find_threat(objects)
        if self.target:
            tx = getattr(self.target, "x", self.owner.x)
            ty = getattr(self.target, "y", self.owner.y)
            self._move_towards(tx, ty, self.intercept_speed, dt)
            if _dist(self.x, self.y, tx, ty) <= self.size * 1.2:
                self.target = None
        else:
            self._patrol(dt)

    def _return(self, dt: float) -> None:
        self._move_towards(self.owner.x, self.owner.y, self.intercept_speed, dt)
        if _dist(self.x, self.y, self.owner.x, self.owner.y) <= self.owner.size * 1.5:
            self._wander_target = None

    def compute_reward(self, objects: list) -> float:
        reward = 0.0
        if self.prev_hp:
            reward -= (self.prev_hp - self.hp)
        d_owner = _dist(self.x, self.y, self.owner.x, self.owner.y)
        if d_owner <= self.patrol_radius:
            reward += 0.05
        else:
            reward -= 0.05
        threat = self._find_threat(objects)
        if threat and _dist(self.x, self.y, getattr(threat, "x", 0), getattr(threat, "y", 0)) <= self.size * 1.5:
            reward += 0.2
        return reward

    # ------------------------------------------------------------------
    # Main update
    # ------------------------------------------------------------------
    def update(self, dt: float, objects: list) -> None:
        if not self.prev_hp:
            self.prev_hp = self.hp
        state = self._state(objects)
        action = self.choose_action(state)
        if action == "patrol":
            self._patrol(dt)
        elif action == "intercept":
            self._intercept(dt, objects)
        else:
            self._return(dt)
        reward = self.compute_reward(objects)
        next_state = self._state(objects)
        self.learn(state, action, reward, next_state)
        self.prev_hp = self.hp
