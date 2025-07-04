from __future__ import annotations

from dataclasses import dataclass, field
import math
import pygame


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


class EMPArtifact(Artifact):
    """Electromagnetic pulse that disables shields in range including the owner's."""

    def __init__(self, radius: float = 300.0) -> None:
        super().__init__("EMP", cooldown=8.0)
        self.radius = radius

    def activate(self, user, enemies: list) -> None:
        if not self.can_use():
            return
        self._timer = 0.0
        user.shield.strength = 0.0
        if getattr(user, "area_shield", None):
            user.area_shield.strength = 0.0
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


class GravityTractorArtifact(Artifact):
    """Spawn a small gravity well that tugs nearby ships."""

    def __init__(self) -> None:
        super().__init__("Gravity Tractor", cooldown=30.0)
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
        from blackhole import TemporaryBlackHole

        self._timer = 0.0
        hole = TemporaryBlackHole(x, y)
        self._pending_user.specials.append(hole)
        self.awaiting_click = False
        self._pending_user = None

