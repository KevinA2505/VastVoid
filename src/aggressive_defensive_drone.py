"""Aggressive drone that patrols the Nebula Order flagship's ring."""

import math

import config
from combat import Drone, Projectile


class AggressiveDefensiveDrone(Drone):
    """A more combative drone orbiting around its owner."""

    def __init__(
        self,
        owner,
        radius: float,
        hp: float = 40.0,
        fire_cooldown: float = 0.3,
        orbit_speed: float = 0.5,
        speed_factor: float = 0.8,
        optimal_range: float = 60.0,
    ) -> None:
        super().__init__(
            owner,
            hp=hp,
            orbit_speed=orbit_speed,
            speed_factor=speed_factor,
        )
        self.radius = radius
        self.fire_cooldown = fire_cooldown
        self.intercept_speed = (
            config.DEF_DRONE_INTERCEPT_SPEED * 0.75 * speed_factor
        )
        self.optimal_range = optimal_range
        self.state = "idle"
        self.target = None

    def update(self, dt: float, targets: list) -> None:
        """Intercept nearby threats while shooting rapidly."""

        self.lifetime -= dt
        if self.state == "idle":
            self.angle += self.orbit_speed * dt
            self.x = self.owner.x + math.cos(self.angle) * self.radius
            self.y = self.owner.y + math.sin(self.angle) * self.radius
            threat = self._find_target(targets)
            if threat:
                self.target = threat.ship
                self.state = "intercept"
        else:
            if isinstance(self.target, object):
                tx = getattr(self.target, "x", self.owner.x)
                ty = getattr(self.target, "y", self.owner.y)
            else:
                tx, ty = self.owner.x, self.owner.y
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy) or 1.0
            if dist > self.optimal_range:
                self.x += (dx / dist * self.intercept_speed) * dt
                self.y += (dy / dist * self.intercept_speed) * dt
            else:
                self.state = "idle"
                self.target = None

        max_dist = self.radius * config.DEF_DRONE_MAX_ROAM_FACTOR
        d_from_owner = math.hypot(self.x - self.owner.x, self.y - self.owner.y)
        if d_from_owner > max_dist:
            angle = math.atan2(self.y - self.owner.y, self.x - self.owner.x)
            self.x = self.owner.x + math.cos(angle) * max_dist
            self.y = self.owner.y + math.sin(angle) * max_dist

        if self._timer > 0:
            self._timer -= dt
        else:
            target = self._find_target(targets)
            if target:
                proj = Projectile(
                    self.x,
                    self.y,
                    target.ship.x,
                    target.ship.y,
                    350,
                    3,
                )
                self.projectiles.append(proj)
                self._timer = self.fire_cooldown

        for proj in list(self.projectiles):
            proj.update(dt)
            if proj.expired():
                self.projectiles.remove(proj)
