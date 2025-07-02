import pygame

class Star:
    """Represents a star in the star system."""

    def __init__(self, x: float, y: float, radius: int, color=(255, 255, 0)) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw the star applying an optional camera offset."""
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius,
        )
