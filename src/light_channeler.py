import math
import random
import pygame
import config
from combat import Weapon, Projectile


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
        self.transfer_rate = config.CHANNELER_TRANSFER_RATE
        self.battery = None
        self.timer = 0.0
        self.hp = config.CHANNELER_HP
        self.max_hp = config.CHANNELER_HP

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
        return self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (255, 240, 150), pos, max(2, int(8 * zoom)))
        bar_w = max(12, int(20 * zoom))
        bar_h = max(2, int(4 * zoom))
        bar_x = pos[0] - bar_w // 2
        bar_y = pos[1] - int(12 * zoom)
        pygame.draw.rect(screen, (60, 60, 90), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
        fill = int(bar_w * max(0.0, min(1.0, self.hp / self.max_hp)))
        if fill > 0:
            pygame.draw.rect(screen, (150, 0, 0), (bar_x, bar_y, fill, bar_h))
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
        self.max_energy = config.BATTERY_MAX_ENERGY
        self.turret = None
        self.timer = 0.0
        self.hp = config.BATTERY_HP
        self.max_hp = config.BATTERY_HP
        self.deploy_delay = config.CHANNELER_BATTERY_DELAY

    def update(self, dt: float) -> None:
        self.timer += dt

    def expired(self) -> bool:
        return self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        if self.timer >= self.deploy_delay:
            pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
            pygame.draw.rect(
                screen,
                (120, 180, 255),
                (pos[0] - int(6 * zoom), pos[1] - int(6 * zoom), int(12 * zoom), int(12 * zoom)),
            )
            bar_w = max(12, int(20 * zoom))
            bar_h = max(2, int(4 * zoom))
            bar_x = pos[0] - bar_w // 2
            bar_y = pos[1] - int(12 * zoom)
            pygame.draw.rect(screen, (60, 60, 90), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
            fill = int(bar_w * max(0.0, min(1.0, self.hp / self.max_hp)))
            if fill > 0:
                pygame.draw.rect(screen, (150, 0, 0), (bar_x, bar_y, fill, bar_h))
            chan_pos = (
                int((self.channeler.x - offset_x) * zoom),
                int((self.channeler.y - offset_y) * zoom),
            )
            pygame.draw.line(screen, (100, 200, 255), pos, chan_pos, max(1, int(2 * zoom)))
            if self.turret and self.turret.timer >= self.turret.deploy_delay:
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
        self.hp = config.STAR_TURRET_HP
        self.max_hp = config.STAR_TURRET_HP
        self.projectiles: list[Projectile] = []
        self._timer = 0.0
        self.connected_rate = config.CADENCE_100_RPM  # seconds between shots
        self.disconnected_rate = config.CADENCE_30_RPM
        self.timer = 0.0
        self.deploy_delay = config.CHANNELER_TURRET_DELAY
        self.arc = config.STAR_TURRET_ARC

    @property
    def connected(self) -> bool:
        return self.battery.channeler is not None

    def update(self, dt: float, targets: list | None = None) -> None:
        self.timer += dt
        if self.timer < self.deploy_delay:
            return
        self._timer += dt
        if not self.connected:
            self.hp -= dt * config.STAR_TURRET_DISCONNECTED_LOSS
        rate = self.connected_rate if self.connected else self.disconnected_rate
        if self._timer >= rate:
            self._timer -= rate
            if (
                self.connected
                and self.battery.energy >= config.STAR_TURRET_ENERGY_PER_SHOT
            ):
                self.battery.energy -= config.STAR_TURRET_ENERGY_PER_SHOT
            ang = self.angle + random.uniform(-self.arc / 2, self.arc / 2)
            proj = Projectile(
                self.x,
                self.y,
                self.x + math.cos(ang),
                self.y + math.sin(ang),
                config.STAR_TURRET_PROJECTILE_SPEED,
                config.STAR_TURRET_PROJECTILE_DAMAGE,
                max_distance=config.STAR_TURRET_PROJECTILE_MAX_DISTANCE,
            )
            self.projectiles.append(proj)
        for proj in list(self.projectiles):
            proj.update(dt)
            hit = False
            if targets:
                for t in targets:
                    if (
                        math.hypot(proj.x - t.ship.x, proj.y - t.ship.y)
                        <= t.ship.collision_radius
                    ):
                        t.ship.take_damage(proj.damage)
                        hit = True
                        break
            if hit or proj.expired():
                self.projectiles.remove(proj)

    def expired(self) -> bool:
        return self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        if self.timer >= self.deploy_delay:
            pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
            pygame.draw.circle(screen, (200, 120, 120), pos, max(3, int(6 * zoom)))
            bar_w = max(12, int(20 * zoom))
            bar_h = max(2, int(4 * zoom))
            bar_x = pos[0] - bar_w // 2
            bar_y = pos[1] - int(12 * zoom)
            pygame.draw.rect(screen, (60, 60, 90), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_w, bar_h), 1)
            fill = int(bar_w * max(0.0, min(1.0, self.hp / self.max_hp)))
            if fill > 0:
                pygame.draw.rect(screen, (150, 0, 0), (bar_x, bar_y, fill, bar_h))
            for proj in self.projectiles:
                proj.draw(screen, offset_x, offset_y, zoom)


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
