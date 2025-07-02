import math
from dataclasses import dataclass, field
import pygame
import config


@dataclass
class Weapon:
    """Simple weapon with a cooldown between shots."""
    name: str
    damage: int
    speed: float
    cooldown: float = 0.5
    _timer: float = field(default=0.0, init=False, repr=False)

    def update(self, dt: float) -> None:
        if self._timer < self.cooldown:
            self._timer += dt

    def can_fire(self) -> bool:
        return self._timer >= self.cooldown

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        return Projectile(x, y, tx, ty, self.speed, self.damage)

    def fire_homing(self, x: float, y: float, target, turn_rate: float = config.HOMING_PROJECTILE_TURN_RATE):
        """Fire a projectile that homes in on ``target``."""
        if not self.can_fire():
            return None
        self._timer = 0.0
        return HomingProjectile(x, y, target, self.speed, self.damage, turn_rate)


class Projectile:
    """Projectile fired by a weapon with optional curvature and range."""

    def __init__(
        self,
        x: float,
        y: float,
        tx: float,
        ty: float,
        speed: float,
        damage: int,
        curvature: float = 0.0,
        max_distance: float = config.PROJECTILE_MAX_DISTANCE,
    ) -> None:
        self.x = x
        self.y = y
        self.damage = damage
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy) or 1.0
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed
        self.curvature = curvature
        self.max_distance = max_distance
        self.traveled = 0.0

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        step = math.hypot(self.vx * dt, self.vy * dt)
        self.traveled += step
        if self.curvature:
            angle = math.atan2(self.vy, self.vx) + self.curvature * dt
            speed = math.hypot(self.vx, self.vy)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed

    def expired(self) -> bool:
        if self.max_distance <= 0:
            return False
        return self.traveled >= self.max_distance

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        radius = max(1, int(3 * zoom))
        pygame.draw.circle(screen, (255, 50, 50), pos, radius)


class HomingProjectile(Projectile):
    """Projectile that gradually turns to follow a moving target."""

    def __init__(
        self,
        x: float,
        y: float,
        target,
        speed: float,
        damage: int,
        turn_rate: float = config.HOMING_PROJECTILE_TURN_RATE,
        max_distance: float = config.PROJECTILE_MAX_DISTANCE,
    ) -> None:
        super().__init__(x, y, target.x, target.y, speed, damage, 0.0, max_distance)
        self.target = target
        self.turn_rate = turn_rate

    def update(self, dt: float) -> None:
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        desired = math.atan2(dy, dx)
        current = math.atan2(self.vy, self.vx)
        diff = (desired - current + math.pi) % (2 * math.pi) - math.pi
        max_turn = self.turn_rate * dt
        if abs(diff) > max_turn:
            current += max_turn if diff > 0 else -max_turn
        else:
            current = desired
        speed = math.hypot(self.vx, self.vy)
        self.vx = math.cos(current) * speed
        self.vy = math.sin(current) * speed
        super().update(dt)


@dataclass
class Shield:
    """Basic energy shield that absorbs damage and recharges over time."""
    max_strength: int = 100
    # Regeneration slowed down so shields take longer to recover
    recharge_rate: float = 1.0
    strength: float = field(init=False)

    def __post_init__(self) -> None:
        self.strength = float(self.max_strength)

    def recharge(self, dt: float) -> None:
        if self.strength < self.max_strength:
            self.strength = min(self.max_strength, self.strength + self.recharge_rate * dt)

    def take_damage(self, amount: float) -> None:
        self.strength = max(0.0, self.strength - amount)
