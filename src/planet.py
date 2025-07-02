import math
import pygame
from star import Star

class Planet:
    """Planet that orbits around a star."""

    def __init__(self, star: Star, distance: float, radius: int, color, angle: float, speed: float) -> None:
        self.star = star
        self.distance = distance
        self.radius = radius
        self.color = color
        self.angle = angle
        self.speed = speed
        self.x = 0.0
        self.y = 0.0
        self.update()

    def update(self) -> None:
        self.angle += self.speed
        self.x = self.star.x + self.distance * math.cos(self.angle)
        self.y = self.star.y + self.distance * math.sin(self.angle)

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius,
        )
