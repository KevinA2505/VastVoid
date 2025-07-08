import math
import random
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
        trail_color: tuple[int, int, int] | None = None,
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
        self.trail_color = trail_color
        self.trail: list[tuple[float, float]] = []

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.trail_color is not None:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 15:
                self.trail.pop(0)
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
        if self.trail_color and len(self.trail) > 1:
            points = [
                (int((px - offset_x) * zoom), int((py - offset_y) * zoom))
                for px, py in self.trail
            ]
            pygame.draw.lines(screen, self.trail_color, False, points, max(1, int(2 * zoom)))
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
        self.speed = speed + 4
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

    def update(self, dt: float, targets: list) -> None:
        if self.state == "probe":
            for obj in targets:
                if self.hits(obj.ship):
                    self.target = obj.ship
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


class Bomb(Projectile):
    """Explosive projectile that detonates on impact."""

    def __init__(
        self,
        x: float,
        y: float,
        tx: float,
        ty: float,
        damage: float = 24.0,
        speed: float = 200.0,
        radius: float = 80.0,
        trail_color: tuple[int, int, int] | None = None,
    ) -> None:
        super().__init__(x, y, tx, ty, speed, damage, 0.0, max_distance=500, trail_color=trail_color)
        self.radius = radius
        self.exploded = False
        self.timer = 0.0

    def update(self, dt: float) -> None:
        if self.exploded:
            self.timer -= dt
        else:
            super().update(dt)
            if self.traveled >= self.max_distance:
                self.explode()

    def explode(self) -> None:
        if not self.exploded:
            self.exploded = True
            self.timer = 0.2

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
        pygame.draw.circle(screen, (150, 80, 30), pos, max(2, int(5 * zoom)))
        if self.exploded:
            pygame.draw.circle(screen, (255, 100, 50), pos, int(self.radius * zoom), 1)


class BombDrone:
    """Slow homing drone that explodes on impact."""

    def __init__(
        self,
        owner,
        direction: float = 0.0,
        hp: float = 40.0,
        speed: float = 80.0,
        lifetime: float = 6.0,
        radius: float = 100.0,
        damage: float = 40.0,
    ) -> None:
        self.owner = owner
        self.target = None
        self.hp = hp
        self.speed = speed
        self.lifetime = lifetime
        self.radius = radius
        self.damage = damage
        self.size = 12
        self.exploded = False
        self.timer = 0.0
        self.x = owner.x
        self.y = owner.y
        self.vx = math.cos(direction) * speed
        self.vy = math.sin(direction) * speed

    def _find_target(self, targets: List):
        if not targets:
            return None
        nearest = None
        min_d = float("inf")
        for obj in targets:
            d = math.hypot(obj.ship.x - self.x, obj.ship.y - self.y)
            if d < min_d:
                min_d = d
                nearest = obj
        return nearest

    def _explode(self) -> None:
        if not self.exploded:
            self.exploded = True
            self.timer = 0.2

    def update(self, dt: float, targets: List) -> None:
        if self.exploded:
            self.timer -= dt
            return
        self.lifetime -= dt
        if self.lifetime <= 0 or self.hp <= 0:
            self._explode()
            return
        target = self._find_target(targets)
        if target:
            dx = target.ship.x - self.x
            dy = target.ship.y - self.y
            dist = math.hypot(dx, dy) or 1.0
            self.vx = dx / dist * self.speed
            self.vy = dy / dist * self.speed
        self.x += self.vx * dt
        self.y += self.vy * dt

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
        pygame.draw.circle(screen, (200, 120, 50), pos, max(2, int(6 * zoom)))
        if self.exploded:
            pygame.draw.circle(screen, (255, 100, 50), pos, int(self.radius * zoom), 1)

class Drone:
    """Autonomous drone that orbits the owner and fires at nearby targets.

    Drones persist until their hit points reach zero rather than expiring
    after a timed duration. A small size value defines a hitbox so projectiles
    can damage them.
    """

    def __init__(
        self,
        owner,
        hp: float = 16.0,
        lifetime: float = float("inf"),
        orbit_speed: float = 2.0,
        speed_factor: float = 1.0,
    ) -> None:
        self.owner = owner
        self.angle = 0.0
        # Increased orbit range so drones keep a bit more distance
        # and engage targets from farther away
        self.radius = owner.size * 4
        self.orbit_speed = orbit_speed * speed_factor
        self.hp = hp
        self.lifetime = lifetime
        self.size = 10
        self.projectiles: List[Projectile] = []
        # Slightly faster fire rate
        self.fire_cooldown = 0.32
        self._timer = 0.0
        self.x = owner.x
        self.y = owner.y

    def update(self, dt: float, targets: List) -> None:
        self.lifetime -= dt
        self.angle += self.orbit_speed * dt
        self.x = self.owner.x + math.cos(self.angle) * self.radius
        self.y = self.owner.y + math.sin(self.angle) * self.radius
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

    def _find_target(self, targets: List):
        nearest = None
        # Increased engagement range
        min_d = 250.0
        for obj in targets:
            d = math.hypot(obj.ship.x - self.x, obj.ship.y - self.y)
            if d < min_d:
                min_d = d
                nearest = obj
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
        self.damage_rate = 8.0

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        angle = math.atan2(ty - y, tx - x)
        return LaserBeam(self.owner, angle, self.beam_length, self.damage_rate)


class MineWeapon(Weapon):
    """Remote bomb drone launcher."""

    def __init__(self) -> None:
        super().__init__("Dron bomba", 0, 0, cooldown=10.0)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        angle = math.atan2(ty - y, tx - x)
        return BombDrone(self.owner, direction=angle)


class DroneWeapon(Weapon):
    """Weapon that releases an assisting drone."""

    def __init__(self) -> None:
        super().__init__("Dron asistente", 0, 0, cooldown=8.5)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        existing = [s for s in getattr(self.owner, "specials", []) if isinstance(s, Drone)]
        if len(existing) >= 3:
            return None
        self._timer = 0.0
        return Drone(self.owner, speed_factor=config.NPC_SPEED_FACTOR)


class MissileWeapon(Weapon):
    """Heavy homing missile launcher."""

    def __init__(self) -> None:
        super().__init__("Misil hiperguiado", 30, 250, cooldown=4.5)
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
        super().__init__("Basic", 6, 380, cooldown=0.6)


class IonSymbiontShot(Projectile):
    """Projectile that attaches to a ship and deals damage over time."""

    def __init__(self, x: float, y: float, tx: float, ty: float, speed: float, damage: float) -> None:
        super().__init__(x, y, tx, ty, speed, damage)
        self.attached = False
        self.target = None
        self.offset = (0.0, 0.0)
        self.timer = 3.0  # deal damage over 3 seconds
        self.exploding = False

    def update(self, dt: float, targets: list | None = None) -> None:
        if self.exploding:
            self.timer -= dt
            return

        if not self.attached:
            super().update(dt)
            if targets:
                for obj in targets:
                    dist = math.hypot(obj.ship.x - self.x, obj.ship.y - self.y)
                    if dist <= obj.ship.collision_radius:
                        self.attached = True
                        self.target = obj.ship
                        self.offset = (self.x - obj.ship.x, self.y - obj.ship.y)
                        break
        else:
            if not self.target or self.target.hull <= 0:
                self.attached = False
                self.exploding = True
                self.timer = 0.2
                return
            self.x = self.target.x + self.offset[0]
            self.y = self.target.y + self.offset[1]
            if self.timer > 0:
                damage_rate = self.damage / 3.0
                self.target.take_damage(damage_rate * dt)
                self.timer -= dt
            if self.timer <= 0:
                self.exploding = True
                self.timer = 0.2

    def expired(self) -> bool:
        return self.exploding and self.timer <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        if self.exploding:
            pygame.draw.circle(screen, (255, 100, 50), pos, max(2, int(6 * zoom)), 1)
        else:
            pygame.draw.circle(screen, (100, 255, 255), pos, max(2, int(4 * zoom)))


class IonizedSymbiontWeapon(Weapon):
    """Charge-based weapon that fires a sticky ion shot."""

    def __init__(self) -> None:
        super().__init__("Ion Symbiont", 18, 300, cooldown=2.0)
        self.max_charge = 3.0
        self._charge = 0.0
        self._charging = False

    def update(self, dt: float) -> None:
        super().update(dt)
        if self._charging:
            self._charge = min(self.max_charge, self._charge + dt)

    @property
    def charge_ratio(self) -> float:
        if not self._charging:
            return 0.0
        return self._charge / self.max_charge

    def start_charging(self) -> None:
        if not self.can_fire() or self._charging:
            return
        self._charging = True
        self._charge = 0.0

    def release(self, x: float, y: float, tx: float, ty: float):
        if not self._charging:
            return None
        ratio = self._charge / self.max_charge if self.max_charge > 0 else 0.0
        dmg = self.damage * (1.0 + ratio)
        self._charging = False
        self._charge = 0.0
        self._timer = 0.0
        return IonSymbiontShot(x, y, tx, ty, self.speed, dmg)


class SlowField:
    """Area that slows ships passing through it."""

    def __init__(self, owner, x: float, y: float, radius: float = 100.0, duration: float = 5.0) -> None:
        self.owner = owner
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.timer = 0.0
        self.slow_factor = 0.8  # 20% speed reduction

    def update(self, dt: float) -> None:
        self.timer += dt

    def apply_slow(self, ship) -> None:
        if ship is self.owner:
            return
        if math.hypot(ship.x - self.x, ship.y - self.y) <= self.radius:
            ship.vx *= self.slow_factor
            ship.vy *= self.slow_factor

    def expired(self) -> bool:
        return self.timer >= self.duration

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        rad = int(self.radius * zoom)
        pygame.draw.circle(screen, (80, 120, 255), pos, rad, 1)


class ChronoTachionicWhip(Weapon):
    """Weapon that can deploy a slowing field then fire weak shots."""

    def __init__(self) -> None:
        base_cd = 0.6
        super().__init__("Chrono Whip", 6, 380, cooldown=base_cd)
        self._base_cd = base_cd
        self.field_cooldown = 10.0
        self._field_timer = self.field_cooldown

    def update(self, dt: float) -> None:
        cd = self._base_cd * (0.9 if self._field_timer < self.field_cooldown else 1.0)
        if self._timer < cd:
            self._timer += dt
        if self._field_timer < self.field_cooldown:
            self._field_timer += dt

    def can_fire(self) -> bool:
        cd = self._base_cd * (0.9 if self._field_timer < self.field_cooldown else 1.0)
        return self._timer >= cd

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        if self._field_timer >= self.field_cooldown:
            self._field_timer = 0.0
            return SlowField(self.owner, tx, ty)
        speed = self.speed * 0.95
        return Projectile(x, y, tx, ty, speed, self.damage)


class _SporeParticle:
    """Small particle emitted by a ``SporeCloud``."""

    def __init__(self, cloud) -> None:
        ang = cloud.angle + random.uniform(-cloud.arc / 2, cloud.arc / 2)
        speed = random.uniform(40.0, 80.0)
        self.vx = math.cos(ang) * speed
        self.vy = math.sin(ang) * speed
        self.x = cloud.x
        self.y = cloud.y
        self.life = random.uniform(0.5, 1.0)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt

    def expired(self) -> bool:
        return self.life <= 0


class SporeCloud:
    """Cone-shaped cloud that damages ships over time."""

    def __init__(
        self,
        owner,
        x: float,
        y: float,
        angle: float,
        radius: float = 120.0,
        arc: float = math.pi / 3,
        duration: float = 3.0,
        damage: float = 6.0,
    ) -> None:
        self.owner = owner
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = radius
        self.arc = arc
        self.duration = duration
        self.damage = damage
        self.timer = 0.0
        self._tick = 0.0
        self.particles: list[_SporeParticle] = []

    def contains(self, ship) -> bool:
        dx = ship.x - self.x
        dy = ship.y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.radius:
            return False
        ang = math.atan2(dy, dx)
        diff = (ang - self.angle + math.pi) % (2 * math.pi) - math.pi
        return abs(diff) <= self.arc / 2

    def update(self, dt: float) -> bool:
        self.timer += dt
        self._tick += dt
        if len(self.particles) < 30:
            self.particles.append(_SporeParticle(self))
        for p in list(self.particles):
            p.update(dt)
            if p.expired():
                self.particles.remove(p)
        if self._tick >= 1.0:
            self._tick -= 1.0
            return True
        return False

    def expired(self) -> bool:
        return self.timer >= self.duration

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        start = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        a1 = self.angle - self.arc / 2
        a2 = self.angle + self.arc / 2
        end1 = (
            int((self.x + math.cos(a1) * self.radius - offset_x) * zoom),
            int((self.y + math.sin(a1) * self.radius - offset_y) * zoom),
        )
        end2 = (
            int((self.x + math.cos(a2) * self.radius - offset_x) * zoom),
            int((self.y + math.sin(a2) * self.radius - offset_y) * zoom),
        )
        pygame.draw.polygon(screen, (120, 160, 80, 60), [start, end1, end2])
        for p in self.particles:
            px = int((p.x - offset_x) * zoom)
            py = int((p.y - offset_y) * zoom)
            alpha = max(0, min(255, int(p.life / 1.0 * 255)))
            surf = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(surf, (120, 200, 120, alpha), (1, 1), 1)
            screen.blit(surf, (px - 1, py - 1))


class SporesWeapon(Weapon):
    """Weapon that releases a damaging spore cloud."""

    def __init__(self) -> None:
        super().__init__("Spores", 0, 0, cooldown=5.0)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        angle = self.owner.angle
        dist = self.owner.size * 2
        sx = self.owner.x + math.cos(angle) * dist
        sy = self.owner.y + math.sin(angle) * dist
        return SporeCloud(self.owner, sx, sy, angle)
