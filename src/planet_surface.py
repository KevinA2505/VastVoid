import pygame
import random
import config


ENV_COLORS = {
    "rocky": (110, 110, 110),
    "desert": (210, 200, 150),
    "forest": (50, 120, 50),
    "ice world": (220, 235, 245),
    "ocean world": (30, 80, 160),
    "lava": (150, 60, 30),
    "gas giant": (160, 120, 180),
    "toxic": (100, 150, 80),
}


class Explorer:
    """Simple on-foot avatar used when exploring a planet surface."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.size = 8
        self.color = (255, 255, 255)

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float, width: int, height: int) -> None:
        speed = 150
        if keys[pygame.K_w]:
            self.y -= speed * dt
        if keys[pygame.K_s]:
            self.y += speed * dt
        if keys[pygame.K_a]:
            self.x -= speed * dt
        if keys[pygame.K_d]:
            self.x += speed * dt
        self.x = max(0, min(width, self.x))
        self.y = max(0, min(height, self.y))

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        rect = pygame.Rect(
            int(self.x - offset_x - self.size / 2),
            int(self.y - offset_y - self.size / 2),
            self.size,
            self.size,
        )
        pygame.draw.rect(screen, self.color, rect)


class PlanetSurface:
    """Procedurally generated 2D map tied to a specific planet."""

    def __init__(self, planet) -> None:
        self.planet = planet
        self.width = 3000
        self.height = 3000
        self.surface = pygame.Surface((self.width, self.height))
        self._generate_map()
        self.ship_pos = (self.width // 2, self.height // 2)
        self.explorer = Explorer(*self.ship_pos)
        self.camera_x = self.explorer.x
        self.camera_y = self.explorer.y
        self.exit_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)

    def _random_variation(self, base: tuple[int, int, int]) -> tuple[int, int, int]:
        return tuple(min(255, max(0, c + random.randint(-30, 30))) for c in base)

    def _generate_map(self) -> None:
        base = ENV_COLORS.get(self.planet.environment, (90, 90, 90))
        self.surface.fill(base)
        for _ in range(2000):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            r = random.randint(20, 60)
            pygame.draw.circle(self.surface, self._random_variation(base), (x, y), r)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        self.explorer.update(keys, dt, self.width, self.height)
        self.camera_x = self.explorer.x
        self.camera_y = self.explorer.y

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        offset_x = self.camera_x - config.WINDOW_WIDTH / 2
        offset_y = self.camera_y - config.WINDOW_HEIGHT / 2
        screen.blit(self.surface, (-offset_x, -offset_y))
        # draw landing ship
        ship_rect = pygame.Rect(
            int(self.ship_pos[0] - offset_x - 10),
            int(self.ship_pos[1] - offset_y - 10),
            20,
            20,
        )
        pygame.draw.rect(screen, (200, 200, 200), ship_rect)
        self.explorer.draw(screen, offset_x, offset_y)
        # exit button
        pygame.draw.rect(screen, (60, 60, 90), self.exit_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.exit_rect, 1)
        txt = font.render("Take Off", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.exit_rect.center)
        screen.blit(txt, txt_rect)
