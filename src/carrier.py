import pygame
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
        hull: int = 350,
        fraction: Fraction | None = None,
    ) -> None:
        super().__init__(x, y, model, hull=hull, speed_factor=0.7)
        self.fraction = fraction
        self.hangars = [None] * 5

    def load_ship(self, ship: Ship) -> bool:
        for i, slot in enumerate(self.hangars):
            if slot is None:
                self.hangars[i] = ship
                return True
        return False

    def deploy_ship(self, index: int) -> Ship | None:
        if 0 <= index < len(self.hangars):
            ship = self.hangars[index]
            self.hangars[index] = None
            return ship
        return None

    def draw(
        self,
        screen: pygame.Surface,
        player_fraction: Fraction | None = None,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        color = self.color if self.fraction is None else self.fraction.color
        outline = tuple(max(0, c - 50) for c in color)
        width = int(self.size * 2 * zoom)
        height = int(self.size * 1.2 * zoom)
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        rect = pygame.Rect(0, 0, width, height)
        rect.center = (cx, cy)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, outline, rect, max(1, int(2 * zoom)))
        if player_fraction and self.fraction and player_fraction == self.fraction:
            aura_r = int(max(width, height) * 0.8)
            aura = pygame.Surface((aura_r * 2, aura_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura, color + (80,), (aura_r, aura_r), aura_r)
            screen.blit(aura, (cx - aura_r, cy - aura_r))

__all__ = ["Carrier"]
