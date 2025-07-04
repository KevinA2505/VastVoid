import pygame
import random
from ..names import get_star_name


class Star:
    """Represents a star in the star system."""

    _id_counter = 1

    # Approximate colours for different spectral classes
    SPECTRAL_COLORS = {
        "O": (155, 176, 255),
        "B": (170, 191, 255),
        "A": (202, 215, 255),
        "F": (248, 247, 255),
        "G": (255, 244, 234),
        "K": (255, 210, 161),
        "M": (255, 204, 111),
    }

    def __init__(
        self,
        x: float,
        y: float,
        radius: int,
        color=(255, 255, 0),
        spectral_type: str = "G",
        brightness: int | None = None,
    ) -> None:
        self.name = get_star_name()
        Star._id_counter += 1
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.spectral_type = spectral_type
        self.brightness = brightness if brightness is not None else radius * 10

    @staticmethod
    def random_star(x: float, y: float) -> "Star":
        """Create a star with randomized properties."""
        spectral_type, color = random.choice(list(Star.SPECTRAL_COLORS.items()))
        radius = random.randint(15, 30)
        brightness = random.randint(50, 200)
        return Star(x, y, radius, color, spectral_type, brightness)

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
        zoom: float = 1.0,
    ) -> None:
        """Draw the star applying an optional camera offset and zoom."""
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            self.color,
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )
