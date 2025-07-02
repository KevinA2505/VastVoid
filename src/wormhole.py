import pygame
import random
import config

class WormHole:
    """Paired anomaly that teleports ships between two points."""

    def __init__(self, x: float, y: float, radius: int | None = None) -> None:
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else config.WORMHOLE_RADIUS
        self.pair: "WormHole" | None = None

    def set_pair(self, other: "WormHole") -> None:
        self.pair = other
        other.pair = self

    @staticmethod
    def random_wormhole(xmin: int, xmax: int, ymin: int, ymax: int) -> "WormHole":
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        return WormHole(x, y)

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        center = (int((self.x - offset_x) * zoom),
                  int((self.y - offset_y) * zoom))
        color = config.WORMHOLE_COLOR
        pygame.draw.circle(screen, color, center, scaled_radius, 1)
        if scaled_radius > 2:
            pygame.draw.circle(screen, color, center, scaled_radius // 2, 1)
