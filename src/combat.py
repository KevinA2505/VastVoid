import math
from dataclasses import dataclass, field
from typing import List
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
    owner: object | None = field(default=None, init=False, repr=False)

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


class GuidedMissile(Projectile):
    """Missile that waits before accelerating towards a target."""

    def __init__(
        self,
        x: float,
        y: float,
        target,
        speed: float,
        damage: int,
        delay: float = 1.0,
        lifetime: float = 5.0,
        turn_rate: float = config.HOMING_PROJECTILE_TURN_RATE,
    ) -> None:
        super().__init__(x, y, target.x, target.y, 0.0, damage, 0.0, max_distance=0)
        self.target = target
        self.speed = speed + 5
        self.delay = delay
        self.lifetime = lifetime
        self.turn_rate = turn_rate

    def update(self, dt: float) -> None:
        if self.lifetime > 0:
            self.lifetime -= dt
        if self.lifetime <= 0:
            return
        if self.delay > 0:
            self.delay -= dt
            if self.delay <= 0:
                dx = self.target.x - self.x
                dy = self.target.y - self.y
                dist = math.hypot(dx, dy) or 1.0
                self.vx = dx / dist * self.speed
                self.vy = dy / dist * self.speed
            return
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
        self.vx = math.cos(current) * self.speed
        self.vy = math.sin(current) * self.speed
        super().update(dt)

    def expired(self) -> bool:
        return self.lifetime <= 0


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


class LaserBeam:
    """Laser beam with probe and channelling phases."""

    def __init__(
        self,
        owner,
        angle: float,
        length: float = 600.0,
        damage_rate: float = 10.0,
        probe_time: float = 1.0,
        channel_time: float = 3.0,
    ) -> None:
        self.owner = owner
        self.angle = angle
        self.length = length
        self.damage_rate = damage_rate
        self.probe_time = probe_time
        self.channel_time = channel_time
        self.timer = probe_time
        self.state = "probe"
        self.target = None
        self.alpha = 255

    def _start_point(self) -> tuple[float, float]:
        return self.owner.x, self.owner.y

    def _end_point(self) -> tuple[float, float]:
        x1, y1 = self._start_point()
        ex = x1 + math.cos(self.angle) * self.length
        ey = y1 + math.sin(self.angle) * self.length
        return ex, ey

    def hits(self, target) -> bool:
        px, py = target.x, target.y
        half = target.size / 2
        x1, y1 = self._start_point()
        x2, y2 = self._end_point()
        dx, dy = x2 - x1, y2 - y1
        denom = dx * dx + dy * dy
        if denom == 0:
            return False
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / denom))
        cx = x1 + dx * t
        cy = y1 + dy * t
        dist = math.hypot(px - cx, py - cy)
        return dist <= half

    def update(self, dt: float, enemies: list) -> None:
        if self.state == "probe":
            for en in enemies:
                if self.hits(en.ship):
                    self.target = en.ship
                    self.state = "channel"
                    self.timer = self.channel_time
                    break
            self.timer -= dt
            if self.timer <= 0 and self.state != "channel":
                self.state = "fizzle"
                self.timer = self.probe_time
        elif self.state == "channel":
            if not self.target or self.target.hull <= 0:
                self.state = "done"
            else:
                sx, sy = self._start_point()
                dx = self.target.x - sx
                dy = self.target.y - sy
                if math.hypot(dx, dy) > self.length:
                    self.state = "done"
                else:
                    self.angle = math.atan2(dy, dx)
                    self.target.take_damage(self.damage_rate * dt)
                    self.timer -= dt
                    if self.timer <= 0:
                        self.state = "done"
        elif self.state == "fizzle":
            self.timer -= dt
            self.alpha = int(255 * (self.timer / self.probe_time))
            if self.timer <= 0:
                self.state = "done"

    def expired(self) -> bool:
        return self.state == "done"

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        start = (int((self.owner.x - offset_x) * zoom), int((self.owner.y - offset_y) * zoom))
        if self.state == "channel" and self.target:
            ex, ey = self.target.x, self.target.y
        else:
            ex, ey = self._end_point()
        end = (int((ex - offset_x) * zoom), int((ey - offset_y) * zoom))
        if self.state == "channel":
            width = max(1, int(5 * zoom))
            color = (255, 100, 100)
            alpha = 255
        elif self.state == "fizzle":
            width = max(1, int(3 * zoom))
            color = (255, 50, 50)
            alpha = max(0, self.alpha)
        else:
            width = max(1, int(3 * zoom))
            color = (255, 50, 50)
            alpha = 200
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(surf, (*color, alpha), start, end, width)
        screen.blit(surf, (0, 0))


class TimedMine:
    """Explosive that detonates after a short delay."""

    def __init__(
        self,
        x: float,
        y: float,
        fuse: float = 5.0,
        radius: float = 80.0,
        damage: float = 30.0,
    ) -> None:
        self.x = x
        self.y = y
        self.timer = fuse
        self.radius = radius
        self.damage = damage
        self.exploded = False

    def update(self, dt: float) -> None:
        if self.exploded:
            self.timer -= dt
        else:
            self.timer -= dt
            if self.timer <= 0:
                self.exploded = True
                self.timer = 0.2  # short aftermath before removal

    def expired(self) -> bool:
        return self.exploded and self.timer <= 0

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        color = (200, 200, 50)
        radius = max(2, int(4 * zoom))
        pygame.draw.circle(screen, color, pos, radius)
        if not self.exploded:
            halo = int(self.radius * max(0.0, self.timer / 5.0) * zoom)
            if halo > 0:
                pygame.draw.circle(screen, (255, 100, 50), pos, halo, 1)
        else:
            pygame.draw.circle(screen, (255, 100, 50), pos, int(self.radius * zoom), 1)


class Drone:
    """Autonomous drone that orbits the owner and fires at enemies."""

    def __init__(self, owner, hp: float = 10.0, lifetime: float = 8.0) -> None:
        self.owner = owner
        self.angle = 0.0
        # Increased orbit range so drones keep a bit more distance
        self.radius = owner.size * 3
        self.hp = hp
        self.lifetime = lifetime
        self.projectiles: List[Projectile] = []
        # Slightly faster fire rate
        self.fire_cooldown = 0.8
        self._timer = 0.0
        self.x = owner.x
        self.y = owner.y

    def update(self, dt: float, enemies: List) -> None:
        self.lifetime -= dt
        self.angle += 2.0 * dt
        self.x = self.owner.x + math.cos(self.angle) * self.radius
        self.y = self.owner.y + math.sin(self.angle) * self.radius
        if self._timer > 0:
            self._timer -= dt
        else:
            target = self._find_target(enemies)
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

    def _find_target(self, enemies: List):
        nearest = None
        min_d = 150.0
        for en in enemies:
            d = math.hypot(en.ship.x - self.x, en.ship.y - self.y)
            if d < min_d:
                min_d = d
                nearest = en
        return nearest

    def expired(self) -> bool:
        return self.hp <= 0 or self.lifetime <= 0

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (150, 150, 255), pos, max(2, int(5 * zoom)))
        for proj in self.projectiles:
            proj.draw(screen, offset_x, offset_y, zoom)


class LaserWeapon(Weapon):
    """Weapon that fires a sustained laser beam."""

    def __init__(self) -> None:
        super().__init__("Laser de rafaga", 0, 0, cooldown=6.0)
        self.beam_length = 600.0
        self.damage_rate = 10.0

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        angle = math.atan2(ty - y, tx - x)
        return LaserBeam(self.owner, angle, self.beam_length, self.damage_rate)


class MineWeapon(Weapon):
    """Weapon that deploys timed mines."""

    def __init__(self) -> None:
        super().__init__("Mina temporizada", 0, 0, cooldown=4.0)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        return TimedMine(x, y)


class DroneWeapon(Weapon):
    """Weapon that releases an assisting drone."""

    def __init__(self) -> None:
        super().__init__("Dron asistente", 0, 0, cooldown=10.0)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        existing = [s for s in getattr(self.owner, "specials", []) if isinstance(s, Drone)]
        if len(existing) >= 3:
            return None
        self._timer = 0.0
        return Drone(self.owner)


class MissileWeapon(Weapon):
    """Heavy homing missile launcher."""

    def __init__(self) -> None:
        super().__init__("Misil hiperguiado", 50, 250, cooldown=4.5)
        self.target = None

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        target = self.target or type("T", (), {"x": tx, "y": ty})()
        self.target = None
        return GuidedMissile(x, y, target, self.speed, self.damage)


class BasicWeapon(Weapon):
    """Generic low damage weapon for starting ships."""

    def __init__(self) -> None:
        super().__init__("Basic", 8, 380, cooldown=0.6)
