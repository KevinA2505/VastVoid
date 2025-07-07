import math
import random
import pickle
import os
from dataclasses import dataclass, field
import pygame

from enemy_learning import LearningEnemy
from enemy import Flee, Defend, Attack, Pursue, Idle, _NullKeys
from artifact import Decoy
from combat import (
    LaserWeapon,
    MineWeapon,
    DroneWeapon,
    MissileWeapon,
    BasicWeapon,
)
import config
from ally_metrics import save_reward_history


Q_TABLE_PATH = "learning_ally_q_table.pkl"
Q_TABLE_VERSION = 2


@dataclass
class LearningAlly(LearningEnemy):
    """Friendly ship learning to assist the player."""

    q_table_version: int = field(default=Q_TABLE_VERSION, init=False, repr=False)
    reward_history: list = field(default_factory=list, init=False, repr=False)
    cumulative_reward: float = field(default=0.0, init=False, repr=False)
    elapsed_time: float = field(default=0.0, init=False, repr=False)

    def build_tree(self) -> None:
        self.actions = {
            "flee": Flee(self),
            "defend": Defend(self),
            "attack": Attack(self),
            "pursue": Pursue(self),
            "idle": Idle(self),
        }
        self.tree = None

    # ------------------------------------------------------------------
    # Q-learning helpers
    # ------------------------------------------------------------------
    def _find_threat(self, hostiles: list) -> object | None:
        for enemy in hostiles:
            d = math.hypot(
                enemy.ship.x - self.player_ship.x,
                enemy.ship.y - self.player_ship.y,
            )
            if d <= self.detection_range:
                return enemy.ship
        return None

    def _state(self, hostiles: list) -> tuple:
        dx = self.player_ship.x - self.ship.x
        dy = self.player_ship.y - self.ship.y
        dist = math.hypot(dx, dy)
        if dist <= self.attack_range:
            dist_cat = 0
        elif dist <= self.detection_range:
            dist_cat = 1
        else:
            dist_cat = 2

        hull_low = self.ship.hull <= self.flee_threshold
        threat = self._find_threat(hostiles)
        player_threat = 1 if threat else 0

        def shield_cat(shield) -> int:
            ratio = shield.strength / shield.max_strength
            if ratio > 0.66:
                return 2
            if ratio > 0.33:
                return 1
            return 0

        ally_shield = shield_cat(self.ship.shield)
        player_shield = shield_cat(self.player_ship.shield)

        threat_dist_cat = 2
        if threat:
            dist_t = math.hypot(threat.x - self.ship.x, threat.y - self.ship.y)
            if dist_t <= self.attack_range:
                threat_dist_cat = 0
            elif dist_t <= self.detection_range:
                threat_dist_cat = 1
            else:
                threat_dist_cat = 2

        near_blackhole = 0
        if getattr(self, "_blackholes", None):
            for hole in self._blackholes:
                d = math.hypot(self.ship.x - hole.x, self.ship.y - hole.y)
                if d <= hole.pull_range:
                    near_blackhole = 1
                    break

        return (
            dist_cat,
            player_threat,
            hull_low,
            ally_shield,
            player_shield,
            threat_dist_cat,
            near_blackhole,
        )

    def compute_reward(self, threat, hostiles: list | None = None) -> float:
        """Return a numeric reward based on the latest transition."""

        reward = 0.0

        # Damage taken by the player or the ally is negative reinforcement
        if self.player_prev_hull:
            reward -= self.player_prev_hull - self.player_ship.hull
        if self.prev_hull:
            reward -= (self.prev_hull - self.ship.hull) * 0.5

        # Staying close to the player is encouraged. Grant a bonus when within a
        # small window around the desired distance.
        dist = math.hypot(
            self.player_ship.x - self.ship.x,
            self.player_ship.y - self.ship.y,
        )
        desired = 150.0
        if abs(dist - desired) <= 30.0:
            reward += 0.1

        if dist <= self.attack_range:
            reward += 0.1
        else:
            reward -= 0.05

        # Bonus for keeping a hostile in firing range
        if threat and math.hypot(threat.x - self.ship.x, threat.y - self.ship.y) <= self.attack_range:
            reward += 0.2

        # Penalise getting too close to a black hole
        if getattr(self, "_blackholes", None):
            for hole in self._blackholes:
                if math.hypot(self.ship.x - hole.x, self.ship.y - hole.y) <= hole.pull_range:
                    reward -= 0.2
                    break

        # Reward successful hits and kills
        if hostiles is not None:
            if not hasattr(self, "_enemy_prev_hulls"):
                self._enemy_prev_hulls = {}
            for en in hostiles:
                prev = self._enemy_prev_hulls.get(en, en.ship.hull)
                if en.ship.hull < prev:
                    reward += 0.3
                if en.ship.hull <= 0 < prev:
                    reward += 1.0
                self._enemy_prev_hulls[en] = en.ship.hull

        return reward

    def save_q_table(self, path: str = Q_TABLE_PATH) -> None:
        with open(path, "wb") as f:
            data = {"version": self.q_table_version, "q_table": self.q_table}
            pickle.dump(data, f)
        save_reward_history(self.reward_history)

    def load_q_table(self, path: str = Q_TABLE_PATH) -> None:
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
                    if isinstance(state, tuple) and len(state) == 3:
                        new_state = state + (1, 1, 2, 0)
                    else:
                        new_state = state
                    new_table[new_state] = actions
                self.q_table = new_table
                self.q_table_version = Q_TABLE_VERSION
            else:
                self.q_table = table
                self.q_table_version = version

    # ------------------------------------------------------------------
    # Main update
    # ------------------------------------------------------------------
    def update(
        self,
        keys,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
        hostiles: list | None = None,
        structures: list | None = None,
    ) -> None:
        threat = self._find_threat(hostiles or [])
        self._blackholes = blackholes
        self.target = threat or self.player_ship
        if isinstance(self.ship.orbit_target, Decoy) and self.ship.orbit_target.expired():
            self.ship.cancel_orbit()
        if not self.prev_hull:
            self.prev_hull = self.ship.hull
        if not self.player_prev_hull:
            self.player_prev_hull = self.player_ship.hull
        if not hasattr(self, "_enemy_prev_hulls"):
            self._enemy_prev_hulls = {}
        state = self._state(hostiles or [])
        action = self.choose_action(state)
        if action == "attack" and threat is None:
            # Don't fire on the player when no hostile target is present
            action = "pursue"
        self.perform_action(action)
        self.ship.update(
            _NullKeys(),
            dt,
            world_width,
            world_height,
            sectors,
            blackholes,
            hostiles,
            structures,
        )
        reward = self.compute_reward(threat, hostiles)
        self.cumulative_reward += reward
        self.elapsed_time += dt
        self.reward_history.append((self.elapsed_time, self.cumulative_reward))
        next_state = self._state(hostiles or [])
        self.learn(state, action, reward, next_state)
        if self.state == "idle" and self.ship.autopilot_target is None:
            self._wander_target = None
        self.prev_hull = self.ship.hull
        self.player_prev_hull = self.player_ship.hull

    def draw_at(
        self,
        screen,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
        player_fraction=None,
        aura_color=None,
    ) -> None:
        """Draw the ally's ship at a given offset and zoom.

        ``LearningAlly`` does not implement its own rendering logic, so this
        simply delegates to the underlying :class:`Ship` instance.  The extra
        parameters mirror :meth:`ship.Ship.draw_at` so callers can provide the
        same values they would when drawing other ships.
        """

        if hasattr(self, "ship"):
            self.ship.draw_at(
                screen,
                offset_x,
                offset_y,
                zoom,
                player_fraction,
                aura_color,
            )
            if self.state:
                font_size = max(12, int(12 * zoom))
                font = pygame.font.Font(None, font_size)
                text = font.render(self.state, True, (0, 0, 0))
                pad = 2
                bubble = pygame.Surface(
                    (text.get_width() + pad * 2, text.get_height() + pad * 2),
                    pygame.SRCALPHA,
                )
                bubble.fill((255, 255, 255, 77))
                bubble.blit(text, (pad, pad))
                cx = int((self.ship.x - offset_x) * zoom)
                cy = int((self.ship.y - offset_y) * zoom)
                x = cx - bubble.get_width() // 2
                y = cy - int(self.ship.size * zoom) - bubble.get_height() - 4
                screen.blit(bubble, (x, y))


class _Region:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height


def create_learning_ally(player_ship, x: float, y: float, model=None):
    """Return a LearningAlly spawned near the player."""
    from ship import Ship, SHIP_MODELS
    from character import Alien, Human, Robot

    species_cls = random.choice([Human, Alien, Robot])
    species = species_cls()
    if model is None:
        model = random.choice(SHIP_MODELS)
    region = _Region(
        0,
        0,
        config.GRID_SIZE * config.SECTOR_WIDTH,
        config.GRID_SIZE * config.SECTOR_HEIGHT,
    )
    ally = LearningAlly(
        Ship(
            x,
            y,
            model,
            hull=80,
            fraction=player_ship.fraction,
            speed_factor=config.NPC_SPEED_FACTOR,
        ),
        species,
        region,
        player_ship.fraction,
    )
    ally.player_ship = player_ship
    ally.load_q_table()
    weapon_cls = random.choice(
        [LaserWeapon, MineWeapon, DroneWeapon, MissileWeapon, BasicWeapon]
    )
    ally.ship.weapons = [weapon_cls()]
    for w in ally.ship.weapons:
        w.owner = ally.ship
        w.cooldown = max(w.cooldown, config.ENEMY_WEAPON_COOLDOWN)
    return ally
