import math
import random
import pygame
import config
from star import Star
from names import get_planet_name, PLANET_ENVIRONMENTS
from biome import BIOMES
from planet_surface import ENV_COLORS

# Each planetary environment favours certain biomes.  The tuples store the
# biome name and its relative weight when picking random biomes for a planet.
ENVIRONMENT_BIOMES: dict[str, list[tuple[str, float]]] = {
    "rocky": [("rocky", 0.6), ("desert", 0.2), ("forest", 0.2)],
    "gas giant": [("rocky", 0.4), ("ice world", 0.3), ("desert", 0.3)],
    "ocean world": [("ocean world", 0.7), ("forest", 0.2), ("ice world", 0.1)],
    "ice world": [("ice world", 0.7), ("rocky", 0.2), ("ocean world", 0.1)],
    "desert": [("desert", 0.7), ("rocky", 0.2), ("lava", 0.1)],
    "lava": [("lava", 0.7), ("rocky", 0.2), ("desert", 0.1)],
    "forest": [("forest", 0.7), ("rocky", 0.2), ("ocean world", 0.1)],
    "toxic": [("lava", 0.5), ("desert", 0.3), ("rocky", 0.2)],
}


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
        weights = ENVIRONMENT_BIOMES.get(environment)
        if weights:
            names, probs = zip(*weights)
            pool_names = list(names)
            pool_probs = list(probs)
            num_biomes = random.randint(1, min(3, len(pool_names)))
            biomes: list[str] = []
            for _ in range(num_biomes):
                choice = random.choices(pool_names, weights=pool_probs, k=1)[0]
                biomes.append(choice)
                idx = pool_names.index(choice)
                pool_names.pop(idx)
                pool_probs.pop(idx)
        else:
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
