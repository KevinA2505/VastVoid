import math
import pygame
from star import Star


class Planet:
    """Planet that orbits around a star."""

    _id_counter = 1

    def __init__(self, star: Star, distance: float, radius: int, color, angle: float, speed: float) -> None:
        self.name = f"Planet {Planet._id_counter}"
        Planet._id_counter += 1
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
