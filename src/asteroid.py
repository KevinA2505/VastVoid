import math
import random
import pygame

# Possible asteroid categories with default color and resource quantity
ASTEROID_TYPES = {
    "rocky": {"color": (110, 110, 110), "resources": 60},
    "metallic": {"color": (140, 140, 160), "resources": 100},
    "icy": {"color": (180, 180, 230), "resources": 40},
}

class Asteroid:
    """Small asteroid that can contain extractable resources."""

    _id_counter = 1

    def __init__(
        self,
        x: float,
        y: float,
        radius: int,
        kind: str = "rocky",
        resources: int | None = None,
    ) -> None:
        self.name = f"Asteroid {Asteroid._id_counter}"
        Asteroid._id_counter += 1
        self.x = x
        self.y = y
        self.radius = radius
        self.kind = kind
        defaults = ASTEROID_TYPES.get(kind, ASTEROID_TYPES["rocky"])
        self.color = defaults["color"]
        self.resources = resources if resources is not None else defaults["resources"]
        # Resistance directly tied to available resources
        self.resistance = float(self.resources)

    @staticmethod
    def random_near_star(star, min_dist: float, max_dist: float) -> "Asteroid":
        """Generate an asteroid positioned around ``star`` within the given range."""
        angle = random.uniform(0, math.tau)
        dist = random.uniform(min_dist, max_dist)
        x = star.x + dist * math.cos(angle)
        y = star.y + dist * math.sin(angle)
        radius = random.randint(2, 5)
        kind = random.choice(list(ASTEROID_TYPES))
        return Asteroid(x, y, radius, kind)

    # ------------------------------------------------------------------
    def mine(self, amount: float) -> None:
        """Reduce resources by ``amount`` and update resistance."""
        self.resources = max(0, self.resources - amount)
        self.resistance = float(self.resources)

    def depleted(self) -> bool:
        return self.resources <= 0

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            self.color,
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )
