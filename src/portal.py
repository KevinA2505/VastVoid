import random
import math
import pygame
import config

class Portal:
    """Green teleportation portal linked in pairs."""
    def __init__(self, x: float, y: float, allowed_faction: str = "Free Explorers", radius: int | None = None, color: tuple[int, int, int] | None = None) -> None:
        self.x = x
        self.y = y
        self.allowed_faction = allowed_faction
        self.radius = radius if radius is not None else config.PORTAL_RADIUS
        self.color = color if color is not None else config.PORTAL_COLOR
        self.pair: "Portal" | None = None

    def set_pair(self, other: "Portal") -> None:
        self.pair = other
        other.pair = self

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        scaled = max(1, int(self.radius * zoom))
        center = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, self.color, center, scaled, 1)
        if scaled > 2:
            pygame.draw.circle(screen, self.color, center, scaled // 2, 1)


def spawn_explorer_portals(free_ship, world_width: int, world_height: int) -> list[Portal]:
    """Create three portal pairs around the Free Explorers flagship."""
    portals: list[Portal] = []
    for _ in range(3):
        ang = random.uniform(0, 2 * math.pi)
        dist = random.uniform(config.PORTAL_NEAR_DISTANCE * 0.5, config.PORTAL_NEAR_DISTANCE)
        x1 = max(0, min(world_width, free_ship.x + math.cos(ang) * dist))
        y1 = max(0, min(world_height, free_ship.y + math.sin(ang) * dist))
        first = Portal(x1, y1)
        for _ in range(100):
            x2 = random.randint(0, world_width)
            y2 = random.randint(0, world_height)
            if math.hypot(x2 - x1, y2 - y1) >= config.PORTAL_PAIR_MIN_DISTANCE:
                second = Portal(x2, y2)
                break
        else:
            x2 = max(0, min(world_width, x1 + config.PORTAL_PAIR_MIN_DISTANCE))
            y2 = y1
            second = Portal(x2, y2)
        first.set_pair(second)
        portals.extend([first, second])
    return portals
