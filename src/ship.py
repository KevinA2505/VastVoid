import pygame
import config

class Ship:
    """Simple controllable ship."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
    ) -> None:
        if keys[pygame.K_w]:
            self.vy -= config.SHIP_ACCELERATION * dt
        if keys[pygame.K_s]:
            self.vy += config.SHIP_ACCELERATION * dt
        if keys[pygame.K_a]:
            self.vx -= config.SHIP_ACCELERATION * dt
        if keys[pygame.K_d]:
            self.vx += config.SHIP_ACCELERATION * dt

        self.vx *= config.SHIP_FRICTION
        self.vy *= config.SHIP_FRICTION

        old_x, old_y = self.x, self.y

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))

        if self._check_collision(sectors):
            self.x, self.y = old_x, old_y
            self.vx = 0
            self.vy = 0

    def _check_collision(self, sectors: list) -> bool:
        half_size = config.SHIP_SIZE / 2
        for sector in sectors:
            if sector.collides_with_point(self.x, self.y, half_size):
                return True
        return False

    def draw(self, screen: pygame.Surface, zoom: float = 1.0) -> None:
        """Draw the ship scaled by a non-linear factor of the zoom level."""
        size = max(1, int(config.SHIP_SIZE * zoom ** 0.5))
        ship_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - size // 2,
            config.WINDOW_HEIGHT // 2 - size // 2,
            size,
            size,
        )
        pygame.draw.rect(screen, config.SHIP_COLOR, ship_rect)
