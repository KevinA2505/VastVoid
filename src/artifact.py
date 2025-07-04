from __future__ import annotations

from dataclasses import dataclass, field
import math
import pygame
import config


@dataclass
class Artifact:
    """Base class for ship artifacts used from the ability bar."""

    name: str
    cooldown: float = 5.0
    _timer: float = field(default=0.0, init=False, repr=False)

    def update(self, dt: float) -> None:
        if self._timer < self.cooldown:
            self._timer += dt

    def can_use(self) -> bool:
        return self._timer >= self.cooldown

    def activate(self, user, enemies: list) -> None:  # pragma: no cover - base
        pass


class AreaShieldAura:
    """Protective bubble that blocks projectiles around a ship."""

    def __init__(self, owner, strength: float = 120.0, radius: float = 80.0) -> None:
        self.owner = owner
        self.strength = strength
        self.radius = radius

    def take_damage(self, amount: float) -> None:
        self.strength = max(0.0, self.strength - amount)

    def expired(self) -> bool:
        return self.strength <= 0.0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (
            int((self.owner.x - offset_x) * zoom),
            int((self.owner.y - offset_y) * zoom),
        )
        pygame.draw.circle(screen, (50, 100, 200), pos, int(self.radius * zoom), 1)


class EMPWave:
    """Short lived visual effect for an EMP blast."""

    def __init__(self, x: float, y: float, radius: float, duration: float = 0.6) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.timer = 0.0

    def update(self, dt: float) -> None:
        self.timer += dt

    def expired(self) -> bool:
        return self.timer >= self.duration

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        progress = min(1.0, self.timer / self.duration)
        cur_radius = self.radius * progress
        alpha = max(0, int(255 * (1.0 - progress)))
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        pos = (
            int((self.x - offset_x) * zoom),
            int((self.y - offset_y) * zoom),
        )
        pygame.draw.circle(surf, (100, 200, 255, alpha), pos, int(cur_radius * zoom), 2)
        screen.blit(surf, (0, 0))


class EMPArtifact(Artifact):
    """Electromagnetic pulse that disables nearby shields."""

    def __init__(self, radius: float = 300.0) -> None:
        super().__init__("EMP", cooldown=8.0)
        self.radius = radius

    def activate(self, user, enemies: list) -> None:
        if not self.can_use():
            return
        self._timer = 0.0
        user.specials.append(EMPWave(user.x, user.y, self.radius))
        for en in enemies:
            dist = math.hypot(en.ship.x - user.x, en.ship.y - user.y)
            if dist <= self.radius:
                en.ship.shield.strength = 0.0
                if getattr(en.ship, "area_shield", None):
                    en.ship.area_shield.strength = 0.0


class AreaShieldArtifact(Artifact):
    """Deploy a temporary protective aura around the ship."""

    def __init__(self) -> None:
        super().__init__("Area Shield", cooldown=12.0)

    def activate(self, user, enemies: list) -> None:
        if not self.can_use():
            return
        self._timer = 0.0
        user.area_shield = AreaShieldAura(user)
        user.specials.append(user.area_shield)


class TractorProbe:
    """Projectile-like probe that deploys a gravity tractor after travel."""

    def __init__(
        self, owner, target_x: float, target_y: float, travel_time: float = 5.0
    ) -> None:
        self.owner = owner
        self.start_x = owner.x
        self.start_y = owner.y
        self.x = self.start_x
        self.y = self.start_y
        self.target_x = target_x
        self.target_y = target_y
        self.duration = travel_time
        self.timer = 0.0
        self.deployed = False

    def update(self, dt: float) -> None:
        if self.deployed:
            return
        self.timer += dt
        progress = min(1.0, self.timer / self.duration)
        self.x = self.start_x + (self.target_x - self.start_x) * progress
        self.y = self.start_y + (self.target_y - self.start_y) * progress
        if self.timer >= self.duration and not self.deployed:
            from blackhole import TemporaryBlackHole

            strength = 15000.0 * 1.25
            lifetime = 15.0 + 15.0
            hole = TemporaryBlackHole(
                self.target_x, self.target_y, strength=strength, lifetime=lifetime
            )
            self.owner.specials.append(hole)
            self.deployed = True

    def expired(self) -> bool:
        return self.deployed

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (200, 200, 50), pos, max(2, int(4 * zoom)))


class GravityTractorArtifact(Artifact):
    """Spawn a small gravity well that tugs nearby ships."""

    def __init__(self) -> None:
        super().__init__("Gravity Tractor", cooldown=35.0)
        self.awaiting_click: bool = False
        self._pending_user = None

    def activate(self, user, enemies: list) -> None:
        if not self.can_use() or self.awaiting_click:
            return
        # Activation now waits for the player to choose a point.
        self.awaiting_click = True
        self._pending_user = user

    def confirm(self, x: float, y: float) -> None:
        """Place the tractor at ``(x, y)`` once the target is chosen."""
        if not self.awaiting_click or not self._pending_user:
            return
        self._timer = 0.0
        probe = TractorProbe(self._pending_user, x, y)
        self._pending_user.specials.append(probe)
        self.awaiting_click = False
        self._pending_user = None

