import math
import pygame
import random
try:
    import noise
except ImportError as exc:
    raise RuntimeError(
        "The 'noise' package is required. "
        "Run 'pip install noise' or install all requirements."
    ) from exc
import config
import control_settings as controls
from biome import BIOMES, Biome



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

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        width: int,
        height: int,
        speed: float = config.EXPLORER_SPEED,
    ) -> None:
        if keys[controls.get_key("move_up")]:
            self.y -= speed * dt
        if keys[controls.get_key("move_down")]:
            self.y += speed * dt
        if keys[controls.get_key("move_left")]:
            self.x -= speed * dt
        if keys[controls.get_key("move_right")]:
            self.x += speed * dt
        # Clamp position so mask lookups stay within bounds
        self.x = max(0, min(width - 1, self.x))
        self.y = max(0, min(height - 1, self.y))

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        rect = pygame.Rect(
            int(self.x - offset_x - self.size / 2),
            int(self.y - offset_y - self.size / 2),
            self.size,
            self.size,
        )
        pygame.draw.rect(screen, self.color, rect)


class Boat:
    """Simple structure spawned when using a boat."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.width = 24
        self.height = 12

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        rect = pygame.Rect(
            int(self.x - offset_x - self.width / 2),
            int(self.y - offset_y - self.height / 2),
            self.width,
            self.height,
        )
        pygame.draw.rect(screen, (180, 120, 60), rect)


class PlanetSurface:
    """Procedurally generated 2D map tied to a specific planet."""

    def __init__(self, planet, player) -> None:
        self.planet = planet
        self.player = player
        self.width = 3000
        self.height = 3000
        self.surface = pygame.Surface((self.width, self.height))
        self.collision_surface = pygame.Surface(
            (self.width, self.height), pygame.SRCALPHA
        )
        self.collision_surface.fill((0, 0, 0, 0))
        self.collision_mask: pygame.mask.Mask | None = None
        self.pickups: list[ItemPickup] = []
        # grid resolution used for walkable map
        self.cell = 60
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
        self.blocked: list[list[bool]] = []
        # Store river segments along with their drawn width
        self.rivers: list[tuple[list[tuple[int, int]], int]] = []
        self.boat_active = False
        self.boat: Boat | None = None
        self._generate_map()
        self.ship_pos = (self.width // 2, self.height // 2)
        self.explorer = Explorer(*self.ship_pos)
        self.camera_x = self.explorer.x
        self.camera_y = self.explorer.y
        self.exit_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.inventory_rect = pygame.Rect(10, 10, 100, 30)

    def _random_variation(self, base: tuple[int, int, int]) -> tuple[int, int, int]:
        """Return the same colour to avoid tonal changes inside a region."""
        return base

    def _draw_patch(self, rect: pygame.Rect, biome: Biome) -> None:
        """Draw a more organic looking patch of terrain."""
        # Randomly choose between an ellipse or an irregular polygon
        if random.random() < 0.5:
            w = int(random.randint(40, 120) * biome.patch_scale)
            h = int(random.randint(30, 80) * biome.patch_scale)
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

    def _draw_tree(self, x: int, y: int, r: int) -> None:
        """Draw a tree made of a small trunk and a round canopy."""
        # Trees are scaled up slightly for a denser look
        r = int(r * 1.38 * 1.15 * 1.2)
        canopy_color = (20, 70, 20)
        trunk_color = (80, 50, 20)
        trunk_width = max(2, r // 2)
        trunk_height = r * 2
        trunk_rect = pygame.Rect(
            x - trunk_width // 2,
            y,
            trunk_width,
            trunk_height,
        )
        pygame.draw.rect(self.surface, trunk_color, trunk_rect)
        # Add collision only for the trunk so canopies don't block movement
        pygame.draw.rect(self.collision_surface, (255, 255, 255), trunk_rect)
        pygame.draw.circle(self.surface, canopy_color, (x, y), r)

    def _draw_river(self) -> None:
        """Draw a wavy blue line representing a river."""
        length = random.randint(self.height // 2, self.height)
        # Rivers are drawn slightly thicker for better visibility
        width = int(random.randint(24, 40) * 1.21 * 1.1)
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
        pygame.draw.lines(
            self.collision_surface, (255, 255, 255), False, points, width
        )
        self.rivers.append((points, width))

    def _draw_river_in_area(self, rect: pygame.Rect) -> None:
        """Draw a short river that flows through the given rectangle."""
        length = random.randint(self.height // 2, self.height)
        width = int(random.randint(24, 40) * 1.21 * 1.1)
        x = random.randint(rect.left, rect.right)
        y = rect.top
        angle = math.pi / 2
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
        pygame.draw.lines(
            self.collision_surface, (255, 255, 255), False, points, width
        )
        self.rivers.append((points, width))

    def _distance_to_segment(
        self, x: float, y: float, p1: tuple[int, int], p2: tuple[int, int]
    ) -> float:
        """Return the distance from point ``(x, y)`` to the line segment ``p1``-``p2``."""
        x1, y1 = p1
        x2, y2 = p2
        if (x1, y1) == (x2, y2):
            return math.hypot(x - x1, y - y1)
        dx = x2 - x1
        dy = y2 - y1
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / float(dx * dx + dy * dy)))
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        return math.hypot(x - proj_x, y - proj_y)

    def _point_near_river(self, x: float, y: float, margin: float = 10.0) -> bool:
        """Return ``True`` if ``(x, y)`` is within ``margin`` of any river."""
        for points, width in self.rivers:
            half = width / 2 + margin
            for i in range(len(points) - 1):
                if self._distance_to_segment(x, y, points[i], points[i + 1]) <= half:
                    return True
        return False

    def _draw_forest(self) -> None:
        """Draw a cluster of trees to represent a forested area."""
        w = int(random.randint(200, 400) * 1.32 * 1.2)
        h = int(random.randint(200, 400) * 1.32 * 1.2)
        x = random.randint(0, self.width - w)
        y = random.randint(0, self.height - h)
        area = pygame.Rect(x, y, w, h)
        has_river = random.random() < 0.3
        if has_river:
            for _ in range(random.randint(1, 2)):
                self._draw_river_in_area(area)
        margin = 0.0
        tree_count = 250
        for _ in range(tree_count):
            tx = random.randint(area.left, area.right)
            ty = random.randint(area.top, area.bottom)
            if self._point_near_river(tx, ty, margin):
                continue
            r = random.randint(3, 8)
            self._draw_tree(tx, ty, r)

        # Scatter some small stones throughout the forest
        for _ in range(30):
            sx = random.randint(area.left, area.right)
            sy = random.randint(area.top, area.bottom)
            if self._point_near_river(sx, sy, margin):
                continue
            sr = random.randint(2, 5)
            pygame.draw.circle(self.surface, (80, 80, 80), (sx, sy), sr)
            pygame.draw.circle(self.collision_surface, (255, 255, 255), (sx, sy), sr)

    def _generate_map(self) -> None:
        """Create a map using 2D noise to assign biomes."""
        cell = self.cell
        cols = self.cols
        rows = self.rows
        self.blocked = [[False for _ in range(cols)] for _ in range(rows)]
        self.surface.fill((0, 0, 0))
        self.collision_surface.fill((0, 0, 0, 0))

        biome_names = (
            self.planet.biomes if self.planet.biomes else [self.planet.environment]
        )
        biomes = [
            BIOMES.get(name, Biome(ENV_COLORS.get(name, (90, 90, 90)), [], 0, 1.0))
            for name in biome_names
        ]

        # Setup noise parameters for biome distribution
        offset_x = random.random() * 1000
        offset_y = random.random() * 1000
        scale = 0.1

        thresholds = [ (i + 1) / len(biomes) for i in range(len(biomes) - 1) ]

        self.pickups.clear()
        is_ocean_planet = self.planet.environment == "ocean world"
        for j in range(rows):
            for i in range(cols):
                nval = noise.pnoise2(i * scale + offset_x, j * scale + offset_y, octaves=3)
                nval = (nval + 1) / 2  # map to [0,1]
                biome_idx = len(biomes) - 1
                for idx, th in enumerate(thresholds):
                    if nval < th:
                        biome_idx = idx
                        break
                biome = biomes[biome_idx]
                rect = pygame.Rect(i * cell, j * cell, cell, cell)
                pygame.draw.rect(self.surface, biome.color, rect)
                if is_ocean_planet or biome_names[biome_idx] == "ocean world":
                    self.blocked[j][i] = True
                    pygame.draw.rect(self.collision_surface, (255, 255, 255), rect)
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

        self.collision_mask = pygame.mask.from_surface(self.collision_surface)

    def is_walkable(self, x: float, y: float) -> bool:
        """Return ``True`` if the coordinates correspond to a walkable cell."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        if self.collision_mask and self.collision_mask.get_at((ix, iy)):
            return self.boat_active
        cx = ix // self.cell
        cy = iy // self.cell
        if 0 <= cx < self.cols and 0 <= cy < self.rows:
            return not self.blocked[cy][cx]
        return False

    def is_water(self, x: float, y: float) -> bool:
        """Return ``True`` if ``(x, y)`` is water based on the collision mask."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        return bool(self.collision_mask and self.collision_mask.get_at((ix, iy)))

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN:
            if event.key == controls.get_key("cancel"):
                return True
            if event.key == controls.get_key("toggle_boat"):
                if self.boat_active:
                    self.boat_active = False
                    self.boat = None
                elif self.player.inventory.get("boat", 0) > 0:
                    self.boat_active = True
                    self.boat = Boat(self.explorer.x, self.explorer.y)
        return False

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        old_x, old_y = self.explorer.x, self.explorer.y
        speed = config.EXPLORER_SPEED
        on_water = self.is_water(self.explorer.x, self.explorer.y)
        if self.boat_active:
            if on_water:
                speed = config.BOAT_SPEED_WATER
            else:
                speed = config.BOAT_SPEED_LAND
            if self.boat:
                self.boat.x = self.explorer.x
                self.boat.y = self.explorer.y
        self.explorer.update(keys, dt, self.width, self.height, speed)
        if not self.is_walkable(self.explorer.x, self.explorer.y):
            self.explorer.x, self.explorer.y = old_x, old_y
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
        # draw landing ship as a small triangle
        cx = int(self.ship_pos[0] - offset_x)
        cy = int(self.ship_pos[1] - offset_y)
        size = 20
        height = size * 1.5
        hx = height / 2
        half_base = size / 2
        angle = -math.pi / 2
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        tip = (cx + cos_a * hx, cy + sin_a * hx)
        left = (
            cx - cos_a * hx - sin_a * half_base,
            cy - sin_a * hx + cos_a * half_base,
        )
        right = (
            cx - cos_a * hx + sin_a * half_base,
            cy - sin_a * hx - cos_a * half_base,
        )
        points = [tip, left, right]
        pygame.draw.polygon(screen, (200, 200, 200), points)
        if self.boat_active and self.boat:
            self.boat.draw(screen, offset_x, offset_y)
        self.explorer.draw(screen, offset_x, offset_y)
        # exit button
        pygame.draw.rect(screen, (60, 60, 90), self.exit_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.exit_rect, 1)
        txt = font.render("Take Off", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.exit_rect.center)
        screen.blit(txt, txt_rect)
        # inventory button
        pygame.draw.rect(screen, (60, 60, 90), self.inventory_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.inventory_rect, 1)
        inv_txt = font.render("Items", True, (255, 255, 255))
        inv_rect = inv_txt.get_rect(center=self.inventory_rect.center)
        screen.blit(inv_txt, inv_rect)
