import random
import math
import pygame
from star_system import StarSystem
from blackhole import BlackHole
from wormhole import WormHole
import config

class Sector:
    """Large region containing multiple star systems."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        num_systems = random.randint(3, 4)
        self.systems = []
        for _ in range(num_systems):
            for _ in range(100):  # attempt placement with spacing
                sx = random.randint(self.x + 100, self.x + self.width - 100)
                sy = random.randint(self.y + 100, self.y + self.height - 100)
                too_close = False
                for system in self.systems:
                    if math.hypot(system.star.x - sx, system.star.y - sy) < config.MIN_SYSTEM_DISTANCE:
                        too_close = True
                        break
                if not too_close:
                    self.systems.append(StarSystem(sx, sy))
                    break

        # Possibly add a black hole positioned far from star systems
        self.blackholes = []
        if random.random() < config.BLACKHOLE_CHANCE:
            for _ in range(100):
                hx = random.randint(self.x + 100, self.x + self.width - 100)
                hy = random.randint(self.y + 100, self.y + self.height - 100)
                too_close = False
                for system in self.systems:
                    if math.hypot(system.star.x - hx, system.star.y - hy) < config.BLACKHOLE_MIN_DISTANCE:
                        too_close = True
                        break
                if not too_close:
                    self.blackholes.append(BlackHole(hx, hy))
                    break

        # Possibly add a worm hole pair positioned far from star systems
        self.wormholes = []
        if random.random() < config.WORMHOLE_CHANCE:
            self._add_wormhole_pair()

    def _add_wormhole_pair(self) -> None:
        """Generate and store a paired set of wormholes in this sector."""
        first = None
        for _ in range(100):
            wx = random.randint(self.x + 100, self.x + self.width - 100)
            wy = random.randint(self.y + 100, self.y + self.height - 100)
            too_close = False
            for system in self.systems:
                if math.hypot(system.star.x - wx, system.star.y - wy) < config.WORMHOLE_MIN_DISTANCE:
                    too_close = True
                    break
            for hole in self.blackholes:
                if math.hypot(hole.x - wx, hole.y - wy) < config.WORMHOLE_MIN_DISTANCE:
                    too_close = True
                    break
            if not too_close:
                first = WormHole(wx, wy)
                break
        if first is None:
            return
        for _ in range(100):
            wx = random.randint(self.x + 100, self.x + self.width - 100)
            wy = random.randint(self.y + 100, self.y + self.height - 100)
            too_close = False
            for system in self.systems:
                if math.hypot(system.star.x - wx, system.star.y - wy) < config.WORMHOLE_MIN_DISTANCE:
                    too_close = True
                    break
            for hole in self.blackholes:
                if math.hypot(hole.x - wx, hole.y - wy) < config.WORMHOLE_MIN_DISTANCE:
                    too_close = True
                    break
            if math.hypot(first.x - wx, first.y - wy) < config.WORMHOLE_MIN_DISTANCE:
                too_close = True
            if not too_close:
                second = WormHole(wx, wy)
                first.set_pair(second)
                self.wormholes.extend([first, second])
                break

    def update(self) -> None:
        for system in self.systems:
            system.update()

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float,
        offset_y: float,
        zoom: float = 1.0,
    ) -> None:
        for system in self.systems:
            system.draw(screen, offset_x, offset_y, zoom)
        for hole in self.blackholes:
            hole.draw(screen, offset_x, offset_y, zoom)
        for hole in self.wormholes:
            hole.draw(screen, offset_x, offset_y, zoom)

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        if not (self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height):
            return False
        for system in self.systems:
            if system.collides_with_point(x, y, radius):
                return True
        for hole in self.blackholes:
            if math.hypot(hole.x - x, hole.y - y) < hole.radius + radius:
                return True
        return False

    def get_object_at_point(self, x: float, y: float, radius: float):
        """Return the star or planet at the given point if any."""
        if not (self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height):
            return None
        for system in self.systems:
            obj = system.get_object_at_point(x, y, radius)
            if obj:
                return obj
        return None


def create_sectors(grid_size: int, width: int, height: int) -> list:
    """Generate a grid of sectors filled with random star systems."""
    sectors = []
    for row in range(grid_size):
        for col in range(grid_size):
            x = col * width
            y = row * height
            sectors.append(Sector(x, y, width, height))

    # Guarantee at least one wormhole pair exists in the world
    if not any(sector.wormholes for sector in sectors):
        random.choice(sectors)._add_wormhole_pair()

    return sectors
