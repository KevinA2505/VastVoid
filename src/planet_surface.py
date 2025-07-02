import math
import pygame
import random
import config
from biome import BIOMES, Biome
from items import ITEM_NAMES


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


class ItemPickup:
    """Collectible item placed on the surface."""

    def __init__(self, name: str, x: float, y: float) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.size = 6

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float,
        offset_y: float,
        font: pygame.font.Font | None = None,
        show_name: bool = False,
    ) -> None:
        rect = pygame.Rect(
            int(self.x - offset_x - self.size / 2),
            int(self.y - offset_y - self.size / 2),
            self.size,
            self.size,
        )
        pygame.draw.rect(screen, (200, 200, 50), rect)
        if show_name and font:
            txt = font.render(self.name, True, (255, 255, 255))
            txt_rect = txt.get_rect(midbottom=(rect.centerx, rect.top - 2))
            screen.blit(txt, txt_rect)


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

    def __init__(self, planet, player) -> None:
        self.planet = planet
        self.player = player
        self.width = 3000
        self.height = 3000
        self.surface = pygame.Surface((self.width, self.height))
        self.pickups: list[ItemPickup] = []
        self._generate_map()
        self.ship_pos = (self.width // 2, self.height // 2)
        self.explorer = Explorer(*self.ship_pos)
        self.camera_x = self.explorer.x
        self.camera_y = self.explorer.y
        self.exit_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)

    def _random_variation(self, base: tuple[int, int, int]) -> tuple[int, int, int]:
        """Return the same colour to avoid tonal changes inside a region."""
        return base

    def _draw_patch(self, rect: pygame.Rect, biome: Biome) -> None:
        """Draw a more organic looking patch of terrain."""
        # Randomly choose between an ellipse or an irregular polygon
        if random.random() < 0.5:
            w = random.randint(40, 120)
            h = random.randint(30, 80)
            x = random.randint(rect.left, rect.right)
            y = random.randint(rect.top, rect.bottom)
            shape = pygame.Rect(x - w // 2, y - h // 2, w, h)
            pygame.draw.ellipse(
                self.surface,
                biome.color,
                shape,
            )
        else:
            points = [
                (
                    random.randint(rect.left, rect.right),
                    random.randint(rect.top, rect.bottom),
                )
                for _ in range(random.randint(3, 6))
            ]
            pygame.draw.polygon(
                self.surface,
                biome.color,
                points,
            )

    def _draw_river(self) -> None:
        """Draw a wavy blue line representing a river."""
        length = random.randint(self.height // 2, self.height)
        width = random.randint(8, 14)
        start_side = random.choice(["top", "bottom", "left", "right"])
        if start_side == "top":
            x, y, angle = random.randint(0, self.width), 0, math.pi / 2
        elif start_side == "bottom":
            x, y, angle = random.randint(0, self.width), self.height, -math.pi / 2
        elif start_side == "left":
            x, y, angle = 0, random.randint(0, self.height), 0
        else:
            x, y, angle = self.width, random.randint(0, self.height), math.pi

        points = [(x, y)]
        seg = 40
        for _ in range(length // seg):
            angle += random.uniform(-0.5, 0.5)
            x += seg * math.cos(angle)
            y += seg * math.sin(angle)
            points.append((int(x), int(y)))
            if x < 0 or x > self.width or y < 0 or y > self.height:
                break
        pygame.draw.lines(self.surface, (50, 100, 200), False, points, width)

    def _draw_forest(self) -> None:
        """Draw a cluster of trees to represent a forested area."""
        w = random.randint(200, 400)
        h = random.randint(200, 400)
        x = random.randint(0, self.width - w)
        y = random.randint(0, self.height - h)
        area = pygame.Rect(x, y, w, h)
        for _ in range(150):
            tx = random.randint(area.left, area.right)
            ty = random.randint(area.top, area.bottom)
            r = random.randint(3, 8)
            pygame.draw.circle(self.surface, (20, 70, 20), (tx, ty), r)

    def _generate_map(self) -> None:
        """Create a map using a simple expansion algorithm for large regions."""
        cell = 60
        cols = self.width // cell
        rows = self.height // cell
        self.surface.fill((0, 0, 0))

        biome_names = (
            self.planet.biomes if self.planet.biomes else [self.planet.environment]
        )
        biomes = [
            BIOMES.get(name, Biome(ENV_COLORS.get(name, (90, 90, 90)), [], 0))
            for name in biome_names
        ]

        grid = [[-1 for _ in range(cols)] for _ in range(rows)]
        queue: list[tuple[int, int, int]] = []
        for idx in range(len(biomes)):
            x = random.randint(0, cols - 1)
            y = random.randint(0, rows - 1)
            grid[y][x] = idx
            queue.append((x, y, idx))

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while queue:
            qidx = random.randrange(len(queue))
            x, y, idx = queue.pop(qidx)
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == -1:
                    grid[ny][nx] = idx
                    queue.append((nx, ny, idx))

        self.pickups.clear()
        for j in range(rows):
            for i in range(cols):
                biome = biomes[grid[j][i]]
                rect = pygame.Rect(i * cell, j * cell, cell, cell)
                pygame.draw.rect(self.surface, biome.color, rect)
                for _ in range(3):
                    self._draw_patch(rect, biome)
                if biome.spawn_items:
                    for _ in range(random.randint(1, 3)):
                        if random.random() < biome.spawn_rate:
                            name = random.choice(biome.spawn_items)
                            px = random.randint(rect.left, rect.right)
                            py = random.randint(rect.top, rect.bottom)
                            self.pickups.append(ItemPickup(name, px, py))

        for _ in range(random.randint(1, 3)):
            self._draw_river()
        for _ in range(random.randint(2, 4)):
            self._draw_forest()

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
        for pickup in self.pickups[:]:
            if (
                abs(self.explorer.x - pickup.x) < 10
                and abs(self.explorer.y - pickup.y) < 10
            ):
                self.player.add_item(pickup.name)
                self.pickups.remove(pickup)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        offset_x = self.camera_x - config.WINDOW_WIDTH / 2
        offset_y = self.camera_y - config.WINDOW_HEIGHT / 2
        screen.blit(self.surface, (-offset_x, -offset_y))
        for pickup in self.pickups:
            show = (
                abs(self.explorer.x - pickup.x) < 40
                and abs(self.explorer.y - pickup.y) < 40
            )
            pickup.draw(screen, offset_x, offset_y, font, show)
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
