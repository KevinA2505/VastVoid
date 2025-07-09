import math
import pygame
from combat import Weapon, SporeCloud


class Channeler:
    """Device that channels energy from the nearest star."""

    def __init__(self, owner) -> None:
        self.owner = owner
        self.star = self._find_star()
        self.angle = 0.0
        if self.star:
            self.angle = math.atan2(owner.y - self.star.y, owner.x - self.star.x)
            dist = self.star.radius + 30
            self.x = self.star.x + math.cos(self.angle) * dist
            self.y = self.star.y + math.sin(self.angle) * dist
        else:
            self.x = owner.x
            self.y = owner.y
        self.transfer_rate = 10.0
        self.battery = None
        self.timer = 0.0

    def _find_star(self):
        nearest = None
        min_d = float("inf")
        for sec in getattr(self.owner, "_sectors", []):
            for system in sec.systems:
                star = system.star
                d = math.hypot(star.x - self.owner.x, star.y - self.owner.y)
                if d < min_d:
                    min_d = d
                    nearest = star
        return nearest

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.star and self.battery:
            transfer = self.transfer_rate * dt
            available = min(transfer, self.star.energy)
            needed = self.battery.max_energy - self.battery.energy
            moved = max(0.0, min(available, needed))
            self.star.energy -= moved
            self.battery.energy += moved

    def expired(self) -> bool:
        return False

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (255, 240, 150), pos, max(2, int(8 * zoom)))
        if self.star:
            end = (
                int((self.star.x - offset_x) * zoom),
                int((self.star.y - offset_y) * zoom),
            )
            pygame.draw.line(screen, (255, 255, 80), pos, end, max(1, int(2 * zoom)))


class Battery:
    """Stores energy transferred from the ``Channeler``."""

    def __init__(self, channeler: Channeler, distance: float = 40.0) -> None:
        self.channeler = channeler
        channeler.battery = self
        self.angle = channeler.angle
        self.x = channeler.x + math.cos(self.angle) * distance
        self.y = channeler.y + math.sin(self.angle) * distance
        self.energy = 0.0
        self.max_energy = 200.0
        self.turret = None

    def update(self, dt: float) -> None:
        pass

    def expired(self) -> bool:
        return False

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.rect(
            screen,
            (120, 180, 255),
            (pos[0] - int(6 * zoom), pos[1] - int(6 * zoom), int(12 * zoom), int(12 * zoom)),
        )
        chan_pos = (
            int((self.channeler.x - offset_x) * zoom),
            int((self.channeler.y - offset_y) * zoom),
        )
        pygame.draw.line(screen, (100, 200, 255), pos, chan_pos, max(1, int(2 * zoom)))
        if self.turret:
            tur_pos = (
                int((self.turret.x - offset_x) * zoom),
                int((self.turret.y - offset_y) * zoom),
            )
            pygame.draw.line(screen, (100, 200, 255), pos, tur_pos, max(1, int(2 * zoom)))


class StarTurret:
    """Turret powered by a ``Battery`` firing spore-like bursts."""

    def __init__(self, battery: Battery, distance: float = 40.0) -> None:
        self.battery = battery
        battery.turret = self
        self.angle = battery.angle
        self.x = battery.x + math.cos(self.angle) * distance
        self.y = battery.y + math.sin(self.angle) * distance
        self.hp = 60.0
        self.projectiles: list[SporeCloud] = []
        self._timer = 0.0
        self.connected_rate = 60.0 / 100.0  # seconds between shots
        self.disconnected_rate = 60.0 / 30.0

    @property
    def connected(self) -> bool:
        return self.battery.channeler is not None

    def update(self, dt: float, targets: list | None = None) -> None:
        self._timer += dt
        if not self.connected:
            self.hp -= dt
        rate = self.connected_rate if self.connected else self.disconnected_rate
        if self._timer >= rate:
            self._timer -= rate
            if self.connected and self.battery.energy >= 1.0:
                self.battery.energy -= 1.0
            ang = self.angle
            if targets:
                nearest = None
                min_d = float("inf")
                for t in targets:
                    d = math.hypot(t.ship.x - self.x, t.ship.y - self.y)
                    if d < min_d:
                        min_d = d
                        nearest = t.ship
                if nearest:
                    ang = math.atan2(nearest.y - self.y, nearest.x - self.x)
            sc = SporeCloud(self, self.x, self.y, ang)
            self.projectiles.append(sc)
        for sc in list(self.projectiles):
            tick = sc.update(dt)
            if tick and targets:
                for t in targets:
                    if sc.contains(t.ship):
                        t.ship.take_damage(sc.damage)
            if sc.expired():
                self.projectiles.remove(sc)

    def expired(self) -> bool:
        return self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (200, 120, 120), pos, max(3, int(6 * zoom)))
        for sc in self.projectiles:
            sc.draw(screen, offset_x, offset_y, zoom)


class LightChannelerWeapon(Weapon):
    """Weapon that deploys a channeler, battery and turret."""

    def __init__(self) -> None:
        super().__init__("Light Channeler", 0, 0, cooldown=8.0)

    def fire(self, x: float, y: float, tx: float, ty: float):
        if not self.can_fire():
            return None
        self._timer = 0.0
        channeler = Channeler(self.owner)
        battery = Battery(channeler)
        turret = StarTurret(battery)
        self.owner.specials.extend([channeler, battery, turret])
        return None


__all__ = ["LightChannelerWeapon"]
