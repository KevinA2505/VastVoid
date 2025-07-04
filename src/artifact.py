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

            # 20% stronger gravitational pull
            strength = 15000.0 * 1.25 * 1.2
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


class RepairNanobots:
    """Swarm that slowly repairs hull and shields."""

    def __init__(self, owner, duration: float = 5.0) -> None:
        self.owner = owner
        self.duration = duration
        self.timer = 0.0
        self.hull_rate = 8.0
        self.shield_rate = 12.0

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.owner.hull < self.owner.max_hull:
            self.owner.hull = min(self.owner.max_hull, self.owner.hull + self.hull_rate * dt)
        shield = self.owner.shield
        if shield.strength < shield.max_strength:
            shield.strength = min(shield.max_strength, shield.strength + self.shield_rate * dt)

    def expired(self) -> bool:
        return self.timer >= self.duration

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.owner.x - offset_x) * zoom), int((self.owner.y - offset_y) * zoom))
        radius = int(self.owner.size * 0.7 * zoom)
        pygame.draw.circle(screen, (100, 255, 100), pos, radius, 1)


class NanobotArtifact(Artifact):
    """Deploy repair nanobots around the ship."""

    def __init__(self) -> None:
        super().__init__("Repair Bots", cooldown=15.0)

    def activate(self, user, enemies: list) -> None:
        if not self.can_use():
            return
        self._timer = 0.0
        user.specials.append(RepairNanobots(user))


class SolarLink:
    """Connect the ship to a nearby star boosting recharge rates."""

    def __init__(self, owner, star, duration: float = 6.0) -> None:
        self.owner = owner
        self.star = star
        self.duration = duration
        self.timer = 0.0
        self._boost = 2.0
        self._weapon_factor = 0.5
        self._prev_rate = owner.shield.recharge_rate
        self._prev_cooldowns = [w.cooldown for w in owner.weapons]
        owner.shield.recharge_rate *= self._boost
        for w in owner.weapons:
            w.cooldown *= self._weapon_factor

    def update(self, dt: float) -> None:
        self.timer += dt

    def expired(self) -> bool:
        if self.timer >= self.duration:
            self.owner.shield.recharge_rate = self._prev_rate
            for w, cd in zip(self.owner.weapons, self._prev_cooldowns):
                w.cooldown = cd
            return True
        return False

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        start = (int((self.owner.x - offset_x) * zoom), int((self.owner.y - offset_y) * zoom))
        end = (int((self.star.x - offset_x) * zoom), int((self.star.y - offset_y) * zoom))
        pygame.draw.line(screen, (255, 255, 100), start, end, max(1, int(2 * zoom)))


class SolarGeneratorArtifact(Artifact):
    """Channel energy from the nearest star if within range."""

    def __init__(self, range_: float = 500.0) -> None:
        super().__init__("Solar Link", cooldown=20.0)
        self.range = range_

    def activate(self, user, enemies: list) -> None:
        if not self.can_use() or not hasattr(user, "_sectors"):
            return
        nearest = None
        min_d = float("inf")
        for sec in user._sectors:
            for system in sec.systems:
                star = system.star
                d = math.hypot(star.x - user.x, star.y - user.y)
                if d < min_d:
                    min_d = d
                    nearest = star
        if nearest is None or min_d > self.range:
            return
        self._timer = 0.0
        user.specials.append(SolarLink(user, nearest))


class Decoy:
    """Fragile copy of the ship that draws enemy fire."""

    def __init__(self, owner, lifetime: float = 6.0, hp: float = 20.0) -> None:
        self.owner = owner
        self.x = owner.x
        self.y = owner.y
        self.size = owner.size
        self.lifetime = lifetime
        self.hp = hp

    def update(self, dt: float, enemies: list) -> None:
        self.lifetime -= dt
        rect = pygame.Rect(
            self.x - self.size / 2,
            self.y - self.size / 2,
            self.size,
            self.size,
        )
        for en in enemies:
            for proj in list(en.ship.projectiles):
                if rect.collidepoint(proj.x, proj.y):
                    self.hp -= proj.damage
                    en.ship.projectiles.remove(proj)
                    if self.hp <= 0:
                        break

    def expired(self) -> bool:
        return self.lifetime <= 0 or self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        rect = pygame.Rect(
            int((self.x - offset_x) * zoom - self.size * zoom / 2),
            int((self.y - offset_y) * zoom - self.size * zoom / 2),
            int(self.size * zoom),
            int(self.size * zoom),
        )
        pygame.draw.rect(screen, (120, 120, 120), rect)


class DecoyArtifact(Artifact):
    """Create a holographic decoy and cloak the user briefly."""

    def __init__(self) -> None:
        super().__init__("Decoy", cooldown=18.0)

    def activate(self, user, enemies: list) -> None:
        if not self.can_use():
            return
        self._timer = 0.0
        user.specials.append(Decoy(user))
        user.invisible_timer = 5.0


# Registry of all artifact types available in the game. This is used by the
# UI to display every artifact even if the player's ship has not equipped it
# yet.
AVAILABLE_ARTIFACTS: list[type[Artifact]] = [
    EMPArtifact,
    AreaShieldArtifact,
    GravityTractorArtifact,
    NanobotArtifact,
    SolarGeneratorArtifact,
    DecoyArtifact,
]

