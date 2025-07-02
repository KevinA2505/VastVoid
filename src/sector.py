import random
import pygame
from star_system import StarSystem

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
            sx = random.randint(self.x + 100, self.x + self.width - 100)
            sy = random.randint(self.y + 100, self.y + self.height - 100)
            self.systems.append(StarSystem(sx, sy))

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

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        if not (self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height):
            return False
        for system in self.systems:
            if system.collides_with_point(x, y, radius):
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
    return sectors
