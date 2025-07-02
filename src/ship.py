import pygame
import config

class Ship:
    """Simple controllable ship."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float, world_width: int, world_height: int) -> None:
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

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))

    def draw(self, screen: pygame.Surface) -> None:
        ship_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - config.SHIP_SIZE // 2,
            config.WINDOW_HEIGHT // 2 - config.SHIP_SIZE // 2,
            config.SHIP_SIZE,
            config.SHIP_SIZE,
        )
        pygame.draw.rect(screen, config.SHIP_COLOR, ship_rect)
