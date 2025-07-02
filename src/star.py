import pygame


class Star:
    """Represents a star in the star system."""

    _id_counter = 1

    def __init__(self, x: float, y: float, radius: int, color=(255, 255, 0)) -> None:
        self.name = f"Star {Star._id_counter}"
        Star._id_counter += 1
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

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
