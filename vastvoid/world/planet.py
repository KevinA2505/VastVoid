import math
import random
import pygame
from .. import config
from .star import Star
from ..names import get_planet_name, PLANET_ENVIRONMENTS
from .biome import BIOMES
from .planet_surface import ENV_COLORS


def _lighter_color(color: tuple[int, int, int], factor: float = 1.3) -> tuple[int, int, int]:
    """Return a lighter variant of ``color`` by the given ``factor``."""
    return tuple(min(255, int(c * factor)) for c in color)


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
        atmosphere_color: tuple[int, int, int] | None = None,
        atmosphere_size: float = 1.5,
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
        self.atmosphere_color = (
            atmosphere_color if atmosphere_color is not None else _lighter_color(color)
        )
        self.atmosphere_size = atmosphere_size
        self.x = 0.0
        self.y = 0.0
        self.update()

    @staticmethod
    def random_planet(
        star: Star,
        distance: float,
        atmosphere_color: tuple[int, int, int] | None = None,
        atmosphere_size: float = 1.5,
    ) -> "Planet":
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
        if atmosphere_color is None:
            atmosphere_color = _lighter_color(color)
        return Planet(
            star,
            distance,
            radius,
            color,
            angle,
            speed,
            environment,
            biomes,
            atmosphere_color,
            atmosphere_size,
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

        # Draw atmosphere halo first so the planet appears on top
        atm_radius = int(self.radius * self.atmosphere_size * zoom)
        if atm_radius > scaled_radius:
            halo = pygame.Surface((atm_radius * 2, atm_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                halo,
                (*self.atmosphere_color, 80),
                (atm_radius, atm_radius),
                atm_radius,
            )
            screen.blit(
                halo,
                (
                    int((self.x - offset_x) * zoom) - atm_radius,
                    int((self.y - offset_y) * zoom) - atm_radius,
                ),
            )

        pygame.draw.circle(
            screen,
            self.color,
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )
