import pygame
import random
import math
from dataclasses import dataclass, field
from ship import Ship
from fraction import Fraction


@dataclass
class Carrier(Ship):
    """Large ship capable of carrying smaller ships."""

    fraction: Fraction | None = None
    hangars: list[Ship | None] = field(default_factory=lambda: [None] * 5)

    def __init__(
        self,
        x: float,
        y: float,
        model=None,
        hull: int = 500,
        fraction: Fraction | None = None,
    ) -> None:
        super().__init__(x, y, model, hull=hull, speed_factor=0.49, fraction=fraction)
        self.fraction = fraction
        self.hangars = [None] * 5

    def load_ship(self, ship: Ship) -> bool:
        """Place ``ship`` in the first empty hangar.

        Moves the ship to the carrier, zeroes its velocity and clears
        autopilot settings. Returns ``True`` if a slot was available.
        """
        for i, slot in enumerate(self.hangars):
            if slot is None:
                self.hangars[i] = ship
                ship.x = self.x
                ship.y = self.y
                ship.vx = 0.0
                ship.vy = 0.0
                ship.autopilot_target = None
                ship.hyperjump_target = None
                return True
        return False

    def deploy_ship(self, index: int) -> Ship | None:
        """Remove the ship at ``index`` and spawn it near the carrier.

        The ship's velocity and autopilot are reset. Returns ``None`` if the
        index is invalid or the hangar is empty.
        """
        if 0 <= index < len(self.hangars):
            ship = self.hangars[index]
            self.hangars[index] = None
            if ship:
                distance = self.collision_radius + ship.collision_radius + 10
                angle = random.uniform(0, 2 * math.pi)
                ship.x = self.x + distance * math.cos(angle)
                ship.y = self.y + distance * math.sin(angle)
                ship.vx = 0.0
                ship.vy = 0.0
                ship.autopilot_target = None
                ship.hyperjump_target = None
            return ship
        return None

    def _rect_points(self, cx: float, cy: float, zoom: float) -> list[tuple[int, int]]:
        """Return the four rotated vertices of the carrier."""
        width = self.size * 2 * zoom
        height = self.size * 1.2 * zoom
        hx = width / 2
        hy = height / 2
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        corners = [(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)]
        points = []
        for dx, dy in corners:
            x = cx + dx * cos_a - dy * sin_a
            y = cy + dx * sin_a + dy * cos_a
            points.append((int(x), int(y)))
        return points

    def draw(
        self,
        screen: pygame.Surface,
        player_fraction: Fraction | None = None,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
        aura_color: tuple[int, int, int] | None = None,
    ) -> None:
        color = self.color if self.fraction is None else self.fraction.color
        outline = tuple(max(0, c - 50) for c in color)
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        points = self._rect_points(cx, cy, zoom)
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, outline, points, max(1, int(2 * zoom)))
        if player_fraction and self.fraction and player_fraction == self.fraction:
            width = self.size * 2 * zoom
            height = self.size * 1.2 * zoom
            aura_r = int(max(width, height) * 0.8)
            aura = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            aura_col = aura_color or color
            pygame.draw.circle(aura, aura_col + (80,), (aura_r, aura_r), aura_r)
            screen.blit(aura, (cx - aura_r, cy - aura_r))

__all__ = ["Carrier"]
