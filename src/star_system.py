import math
import random
import pygame
from star import Star
from planet import Planet
import config

class StarSystem:
    """Collection of a star with orbiting planets."""

    def __init__(self, x: int, y: int) -> None:
        self.star = Star(x, y, random.randint(15, 30))
        self.planets = []
        num_planets = random.randint(2, 5)
        distances = sorted(random.randint(40, 120) for _ in range(num_planets))
        for distance in distances:
            radius = random.randint(4, 10)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            angle = random.uniform(0, 2 * math.pi)
            speed = config.ORBIT_SPEED_FACTOR / math.sqrt(distance)
            self.planets.append(
                Planet(self.star, distance, radius, color, angle, speed)
            )

    def update(self) -> None:
        for planet in self.planets:
            planet.update()

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        if math.hypot(self.star.x - x, self.star.y - y) < self.star.radius + radius:
            return True
        for planet in self.planets:
            if math.hypot(planet.x - x, planet.y - y) < planet.radius + radius:
                return True
        return False

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        self.star.draw(screen, offset_x, offset_y)
        for planet in self.planets:
            planet.draw(screen, offset_x, offset_y)
