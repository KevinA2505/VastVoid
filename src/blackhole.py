import pygame
import math
import random
import config

class BlackHole:
    """Dangerous anomaly that pulls nearby ships."""

    def __init__(self, x: float, y: float, radius: int = None,
                 pull_range: int = None, strength: float = None) -> None:
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else config.BLACKHOLE_RADIUS
        self.pull_range = pull_range if pull_range is not None else config.BLACKHOLE_RANGE
        self.strength = strength if strength is not None else config.BLACKHOLE_STRENGTH

    @staticmethod
    def random_blackhole(xmin: int, xmax: int, ymin: int, ymax: int):
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        return BlackHole(x, y)

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        center = (int((self.x - offset_x) * zoom),
                  int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (10, 10, 10), center, scaled_radius)
        pygame.draw.circle(screen, (80, 0, 80), center, scaled_radius, 1)

