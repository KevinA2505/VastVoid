import pygame
import math
import random
import config

class BlackHole:
    """Dangerous anomaly that pulls nearby ships."""

    def __init__(self, x: float, y: float, radius: int = None,
                 pull_range: int = None, strength: float = None) -> None:
        self.x = x
        self.y = y
        self.radius = radius if radius is not None else config.BLACKHOLE_RADIUS
        self.pull_range = pull_range if pull_range is not None else config.BLACKHOLE_RANGE
        self.strength = strength if strength is not None else config.BLACKHOLE_STRENGTH

    @staticmethod
    def random_blackhole(xmin: int, xmax: int, ymin: int, ymax: int):
        x = random.randint(xmin, xmax)
        y = random.randint(ymin, ymax)
        return BlackHole(x, y)

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        center = (
            int((self.x - offset_x) * zoom),
            int((self.y - offset_y) * zoom),
        )
        pygame.draw.circle(screen, (10, 10, 10), center, scaled_radius)

        # Add a faint swirling halo for a more dramatic look
        for i in range(1, 4):
            halo_radius = scaled_radius + i * int(5 * zoom)
            halo = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
            color = (80, 0, 120, max(30, 90 - i * 20))
            pygame.draw.circle(halo, color, (halo_radius, halo_radius), halo_radius, 2)
            screen.blit(halo, (center[0] - halo_radius, center[1] - halo_radius))

        pygame.draw.circle(screen, (80, 0, 80), center, scaled_radius, 1)

        # visualize the pull range for debugging
        if self.pull_range * zoom > 1:
            range_radius = int(self.pull_range * zoom)
            pygame.draw.circle(screen, (40, 0, 40), center, range_radius, 1)

    def apply_pull(self, ship, dt: float) -> None:
        """Apply gravitational pull on the given ship."""
        dx = self.x - ship.x
        dy = self.y - ship.y
        dist = math.hypot(dx, dy)
        if dist < self.pull_range and dist > 0:
            pull = self.strength / dist
            ship.vx += dx / dist * pull * dt
            ship.vy += dy / dist * pull * dt


class TemporaryBlackHole(BlackHole):
    """A short-lived version of ``BlackHole`` used by artifacts."""

    def __init__(
        self,
        x: float,
        y: float,
        radius: int = 15,
        pull_range: int = 253,  # 15% larger pull range for artifact holes
        strength: float = 15000.0,
        lifetime: float = 15.0,
    ) -> None:
        super().__init__(x, y, radius, pull_range, strength)
        self.lifetime = lifetime

    def update(self, dt: float) -> None:
        self.lifetime -= dt

    def expired(self) -> bool:
        return self.lifetime <= 0

