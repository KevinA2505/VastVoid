import math
import random
import pygame
from star import Star
from planet import Planet
import config

class StarSystem:
    """Collection of a star with orbiting planets."""

    _id_counter = 1

    def __init__(self, x: int, y: int) -> None:
        self.name = f"System {StarSystem._id_counter}"
        StarSystem._id_counter += 1
        self.star = Star(x, y, random.randint(15, 30))
        self.planets = []
        num_planets = random.randint(2, 5)

        # Starting distance ensures planets don't overlap the star
        distance = self.star.radius + 40
        for _ in range(num_planets):
            radius = random.randint(4, 10)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            angle = random.uniform(0, 2 * math.pi)
            # Randomize direction so planets don't all rotate the same way
            speed = random.choice([-1, 1]) * config.ORBIT_SPEED_FACTOR / math.sqrt(distance)

            self.planets.append(
                Planet(self.star, distance, radius, color, angle, speed)
            )

            # Increment distance so orbits are spaced apart
            distance += random.randint(30, 50)

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

    def get_object_at_point(self, x: float, y: float, radius: float):
        """Return the star or planet under the point if any."""
        if math.hypot(self.star.x - x, self.star.y - y) < self.star.radius + radius:
            return self.star
        for planet in self.planets:
            if math.hypot(planet.x - x, planet.y - y) < planet.radius + radius:
                return planet
        return None

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
        zoom: float = 1.0,
    ) -> None:
        self.star.draw(screen, offset_x, offset_y, zoom)
        for planet in self.planets:
            # Draw orbit path for visualization
            pygame.draw.circle(
                screen,
                (80, 80, 120),
                (
                    int((self.star.x - offset_x) * zoom),
                    int((self.star.y - offset_y) * zoom),
                ),
                int(planet.distance * zoom),
                1,
            )
            planet.draw(screen, offset_x, offset_y, zoom)
