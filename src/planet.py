import math
import random
import pygame
import config
from star import Star
from names import get_planet_name, PLANET_ENVIRONMENTS
from biome import BIOMES
from planet_surface import ENV_COLORS


class Planet:
    """Planet that orbits around a star."""

    _id_counter = 1

    def __init__(
        self,
        star: Star,
        distance: float,
        radius: int,
        color,
        angle: float,
        speed: float,
        environment: str = "rocky",
        biomes: list[str] | None = None,
    ) -> None:
        self.name = get_planet_name()
        Planet._id_counter += 1
        self.star = star
        self.distance = distance
        self.radius = radius
        self.color = color
        self.angle = angle
        self.speed = speed
        self.environment = environment
        self.biomes = biomes if biomes is not None else []
        self.x = 0.0
        self.y = 0.0
        self.update()

    @staticmethod
    def random_planet(star: Star, distance: float) -> "Planet":
        """Create a planet with randomised properties."""
        radius = random.randint(4, 10)
        environment = random.choice(PLANET_ENVIRONMENTS)
        fallback_random_color = (
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        )
        color = ENV_COLORS.get(environment, fallback_random_color)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.choice([-1, 1]) * config.ORBIT_SPEED_FACTOR / math.sqrt(distance)
        biome_names = list(BIOMES.keys())
        num_biomes = random.randint(1, min(3, len(biome_names)))
        biomes = random.sample(biome_names, k=num_biomes)
        return Planet(
            star, distance, radius, color, angle, speed, environment, biomes
        )

    def update(self) -> None:
        self.angle += self.speed
        self.x = self.star.x + self.distance * math.cos(self.angle)
        self.y = self.star.y + self.distance * math.sin(self.angle)

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
        zoom: float = 1.0,
    ) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            self.color,
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )
