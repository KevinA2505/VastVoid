import math
from dataclasses import dataclass, field
import pygame


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


class Projectile:
    """Projectile fired by a weapon."""

    def __init__(self, x: float, y: float, tx: float, ty: float, speed: float, damage: int) -> None:
        self.x = x
        self.y = y
        self.damage = damage
        dx = tx - x
        dy = ty - y
        dist = math.hypot(dx, dy) or 1.0
        self.vx = dx / dist * speed
        self.vy = dy / dist * speed

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        radius = max(1, int(3 * zoom))
        pygame.draw.circle(screen, (255, 50, 50), pos, radius)


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
