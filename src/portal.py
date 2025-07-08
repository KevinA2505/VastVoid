import pygame
import random
import math
import config

class Portal:
    """Simple teleportation gate that links to another portal."""

    def __init__(self, x: float, y: float, radius: int | None = None) -> None:
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else config.PORTAL_RADIUS
        self.color = config.PORTAL_COLOR
        self.pair: "Portal" | None = None

    def set_pair(self, other: "Portal") -> None:
        self.pair = other
        other.pair = self

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        scaled = max(1, int(self.radius * zoom))
        center = (
            int((self.x - offset_x) * zoom),
            int((self.y - offset_y) * zoom),
        )
        pygame.draw.circle(screen, self.color, center, scaled, 1)
        if scaled > 2:
            pygame.draw.circle(screen, self.color, center, scaled // 2, 1)


def spawn_explorer_portals(free_ship, world_width: int, world_height: int) -> list[Portal]:
    """Create three paired portals around ``free_ship`` and across the world."""
    portals: list[Portal] = []
    for _ in range(3):
        ang = random.uniform(0, math.tau)
        dist = random.uniform(60, 90)
        near = Portal(
            free_ship.x + math.cos(ang) * dist,
            free_ship.y + math.sin(ang) * dist,
        )
        far = Portal(
            random.randint(0, world_width),
            random.randint(0, world_height),
        )
        near.set_pair(far)
        portals.extend([near, far])
    return portals
