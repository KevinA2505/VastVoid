import pygame
import random
import math
from station import SpaceStation
import config


class AbandonedStation(SpaceStation):
    """Space station variant found drifting inside dust clouds."""

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            (120, 120, 150),
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )


class DustCloud:
    """Large cloudy region that hinders visibility."""

    def __init__(self, x: float, y: float, radius: int,
                 station: AbandonedStation | None = None) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.station = station

    @staticmethod
    def random_cloud(xmin: int, xmax: int, ymin: int, ymax: int) -> "DustCloud":
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        radius = random.randint(
            config.DUST_CLOUD_MIN_RADIUS, config.DUST_CLOUD_MAX_RADIUS
        )
        station = None
        if random.random() < config.ABANDONED_STATION_CHANCE:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.randint(0, radius // 2)
            sx = x + int(math.cos(angle) * dist)
            sy = y + int(math.sin(angle) * dist)
            station = AbandonedStation(sx, sy)
        return DustCloud(x, y, radius, station)

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        if self.station:
            self.station.draw(screen, offset_x, offset_y, zoom)
        scaled_radius = max(1, int(self.radius * zoom))
        surf = pygame.Surface((scaled_radius * 2, scaled_radius * 2), pygame.SRCALPHA)
        color = (*config.DUST_CLOUD_COLOR, 100)
        pygame.draw.circle(surf, color, (scaled_radius, scaled_radius), scaled_radius)
        screen.blit(
            surf,
            (
                int((self.x - offset_x) * zoom) - scaled_radius,
                int((self.y - offset_y) * zoom) - scaled_radius,
            ),
        )
