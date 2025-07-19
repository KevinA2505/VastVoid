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
        self.max_health = config.EXPLORER_MAX_HEALTH
        self.health = config.EXPLORER_MAX_HEALTH

    def take_damage(self, amount: float) -> None:
        """Reduce health by ``amount`` without dropping below zero."""
        self.health = max(0, self.health - amount)

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        width: int,
        height: int,
        speed: float = config.EXPLORER_SPEED,
        in_gas: bool = False,
        has_suit: bool = False,
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
        if in_gas and not has_suit:
            self.take_damage(config.TOXIC_GAS_DAMAGE * dt)

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


class Creature:
    """Simple creature that may wander or chase the explorer."""

    def __init__(
        self,
        x: float,
        y: float,
        world_w: int,
        world_h: int,
        *,
        hostile: bool = False,
    ) -> None:
        self.x = x
        self.y = y
        self.world_w = world_w
        self.world_h = world_h
        self.size = 10
        self.hostile = hostile
        self.color = (180, 60, 60) if hostile else (60, 180, 80)
        self.speed = 40.0
        self.vx = 0.0
        self.vy = 0.0

    def update(self, target_x: float, target_y: float, dt: float) -> None:
        if self.hostile:
            dx = target_x - self.x
            dy = target_y - self.y
            dist = math.hypot(dx, dy)
            if dist < 200 and dist > 0:
                self.vx = (dx / dist) * self.speed
                self.vy = (dy / dist) * self.speed
            else:
                self.vx *= 0.9
                self.vy *= 0.9
        else:
            if random.random() < 0.02:
                ang = random.uniform(0, 2 * math.pi)
                self.vx = math.cos(ang) * self.speed
                self.vy = math.sin(ang) * self.speed
            self.vx *= 0.98
            self.vy *= 0.98

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = max(0, min(self.world_w - 1, self.x))
        self.y = max(0, min(self.world_h - 1, self.y))

    def draw(self, screen: pygame.Surface, off_x: float, off_y: float) -> None:
        rect = pygame.Rect(
            int(self.x - off_x - self.size / 2),
            int(self.y - off_y - self.size / 2),
            self.size,
            self.size,
        )
        pygame.draw.rect(screen, self.color, rect)


class HealingPlant:
    """Plant that restores health when touched."""

    def __init__(self, x: float, y: float, amount: float = 20.0) -> None:
        self.x = x
        self.y = y
        self.amount = amount
        self.radius = 8

    def interact(self, explorer: "Explorer") -> None:
        explorer.health = min(explorer.max_health, explorer.health + self.amount)

    def draw(self, screen: pygame.Surface, off_x: float, off_y: float) -> None:
        rect = pygame.Rect(
            int(self.x - off_x - self.radius),
            int(self.y - off_y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )
        pygame.draw.ellipse(screen, (100, 220, 100), rect)


class FloatingPlatform:
    """Small solid platform hovering within a gas giant."""

    def __init__(self, x: float, y: float, radius: int) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (200, 200, 200)

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius,
        )


class WasteDeposit:
    """Toxic residue that can be collected at a health cost."""

    def __init__(self, x: float, y: float, radius: int) -> None:
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen: pygame.Surface, off_x: float, off_y: float) -> None:
        pygame.draw.circle(
            screen,
            (120, 140, 60),
            (int(self.x - off_x), int(self.y - off_y)),
            self.radius,
        )


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
        self.storm_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.storm_surface.fill((0, 0, 0, 0))
        self.ice_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.ice_surface.fill((0, 0, 0, 0))
        self.desert_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.desert_surface.fill((0, 0, 0, 0))
        self.lava_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.lava_surface.fill((0, 0, 0, 0))
        self.gas_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.gas_surface.fill((0, 0, 0, 0))
        self.collision_mask: pygame.mask.Mask | None = None
        self.storm_mask: pygame.mask.Mask | None = None
        self.ice_mask: pygame.mask.Mask | None = None
        self.lava_mask: pygame.mask.Mask | None = None
        self.gas_mask: pygame.mask.Mask | None = None
        self.desert_storm_active = False
        self.desert_storm_time = 0.0
        self.desert_storm_cooldown = random.uniform(
            config.DESERT_STORM_INTERVAL_MIN, config.DESERT_STORM_INTERVAL_MAX
        )
        self.pickups: list[ItemPickup] = []
        self.healing_plants: list[HealingPlant] = []
        self.creatures: list[Creature] = []
        self.platforms: list[FloatingPlatform] = []
        self.waste_deposits: list[WasteDeposit] = []
        # grid resolution used for walkable map
        self.cell = 60
        self.cols = self.width // self.cell
        self.rows = self.height // self.cell
        self.blocked: list[list[bool]] = []
        # Store river segments along with their drawn width
        self.rivers: list[tuple[list[tuple[int, int]], int]] = []
        self.lava_geysers: list[dict] = []
        self.boat_active = False
        self.boat: Boat | None = None
        self._generate_map()
        self._spawn_unique_plants()
        self._spawn_creatures()
        if self.planet.environment == "ocean world":
            self._spawn_underwater_creatures()
        if self.planet.environment == "lava":
            self._spawn_lava_geysers()
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

    def _forest_palette(
        self, base: tuple[int, int, int]
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        """Return canopy and trunk colours based on the given biome colour."""
        r, g, b = base
        canopy = (
            max(0, min(255, int(r * 0.3 + 20))),
            max(0, min(255, int(g * 0.7 + 60))),
            max(0, min(255, int(b * 0.3 + 20))),
        )
        trunk = (
            max(0, min(255, int(r * 0.5 + 40))),
            max(0, min(255, int(g * 0.3 + 30))),
            max(0, min(255, int(b * 0.1 + 20))),
        )
        return canopy, trunk

    def _draw_tree(
        self,
        x: int,
        y: int,
        r: int,
        canopy_color: tuple[int, int, int] | None = None,
        trunk_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw a tree made of a small trunk and a round canopy."""
        # Trees are scaled up slightly for a denser look and then increased by
        # an additional 10% as requested
        r = int(r * 1.38 * 1.15 * 1.2 * 1.10)
        if canopy_color is None:
            canopy_color = (20, 70, 20)
        if trunk_color is None:
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
        # Add collision only for the lower half of the trunk so canopies do not
        # block movement and only the bottom portion collides
        collision_rect = trunk_rect.copy()
        collision_rect.height //= 2
        collision_rect.top += trunk_height // 2
        pygame.draw.rect(self.collision_surface, (255, 255, 255), collision_rect)
        pygame.draw.circle(self.surface, canopy_color, (x, y), r)

    def _draw_river(
        self,
        color: tuple[int, int, int] = (50, 100, 200),
        damage: bool = False,
        block: bool = True,
    ) -> None:
        """Draw a wavy line representing a river or lava flow."""
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
        pygame.draw.lines(self.surface, color, False, points, width)
        if block:
            pygame.draw.lines(
                self.collision_surface, (255, 255, 255), False, points, width
            )
        if damage:
            pygame.draw.lines(
                self.lava_surface, (200, 60, 60, 180), False, points, width
            )
        self.rivers.append((points, width))
        self._plant_trees_along_river(points, width)

    def _draw_river_in_area(
        self,
        rect: pygame.Rect,
        color: tuple[int, int, int] = (50, 100, 200),
        damage: bool = False,
        block: bool = True,
    ) -> None:
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
        pygame.draw.lines(self.surface, color, False, points, width)
        if block:
            pygame.draw.lines(
                self.collision_surface, (255, 255, 255), False, points, width
            )
        if damage:
            pygame.draw.lines(
                self.lava_surface, (200, 60, 60, 180), False, points, width
            )
        self.rivers.append((points, width))
        self._plant_trees_along_river(points, width)

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

    def _plant_trees_along_river(self, points: list[tuple[int, int]], width: int) -> None:
        """Plant trees along both sides of a river without covering the water."""
        spacing = 60
        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            seg_len = math.hypot(dx, dy)
            if seg_len == 0:
                continue
            steps = max(1, int(seg_len // spacing))
            for _ in range(steps):
                t = random.random()
                px = p1[0] + dx * t
                py = p1[1] + dy * t
                norm_x = -dy / seg_len
                norm_y = dx / seg_len
                offset = width / 2 + random.randint(10, 20)
                for side in (-1, 1):
                    tx = px + norm_x * offset * side
                    ty = py + norm_y * offset * side
                    if self._point_near_river(tx, ty, 0):
                        continue
                    ix, iy = int(tx), int(ty)
                    if not (0 <= ix < self.width and 0 <= iy < self.height):
                        continue
                    r = random.randint(3, 8)
                    base_color = self.surface.get_at((ix, iy))[:3]
                    canopy, trunk = self._forest_palette(base_color)
                    self._draw_tree(ix, iy, r, canopy, trunk)

    def _point_in_polygon(self, x: int, y: int, poly: list[tuple[int, int]]) -> bool:
        """Return ``True`` if ``(x, y)`` lies inside polygon ``poly``."""
        inside = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi
            ):
                inside = not inside
            j = i
        return inside

    def _draw_forest(self, extra_dense: bool = False) -> None:
        """Draw a cluster of trees to represent a forested area."""
        w = int(random.randint(200, 400) * 1.32 * 1.2)
        h = int(random.randint(200, 400) * 1.32 * 1.2)
        x = random.randint(0, self.width - w)
        y = random.randint(0, self.height - h)
        area = pygame.Rect(x, y, w, h)
        has_river = random.random() < 0.3
        if has_river:
            for _ in range(random.randint(1, 2)):
                if self.planet.environment == "lava":
                    self._draw_river_in_area(area, color=(180, 40, 40), damage=True)
                else:
                    self._draw_river_in_area(area)
        margin = 0.0
        tree_count = 250
        if extra_dense:
            tree_count = int(tree_count * 1.5)
        base_color = self.surface.get_at(area.center)[:3]
        canopy_color, trunk_color = self._forest_palette(base_color)
        for _ in range(tree_count):
            tx = random.randint(area.left, area.right)
            ty = random.randint(area.top, area.bottom)
            if self._point_near_river(tx, ty, margin):
                continue
            r = random.randint(3, 8)
            self._draw_tree(tx, ty, r, canopy_color, trunk_color)

        # Scatter some small stones throughout the forest
        for _ in range(30):
            sx = random.randint(area.left, area.right)
            sy = random.randint(area.top, area.bottom)
            if self._point_near_river(sx, sy, margin):
                continue
            sr = random.randint(2, 5)
            pygame.draw.circle(self.surface, (80, 80, 80), (sx, sy), sr)
            pygame.draw.circle(self.collision_surface, (255, 255, 255), (sx, sy), sr)

    def _draw_crater_field(self) -> None:
        """Draw several irregular craters that may contain rare minerals."""
        minerals = ["platino", "diamante", "iridio", "uranio", "palladium"]
        num_craters = random.randint(5, 10)
        cave_entries: list[tuple[int, int]] = []
        for _ in range(num_craters):
            r = random.randint(20, 60)
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - r)
            steps = random.randint(8, 12)
            points: list[tuple[int, int]] = []
            for i in range(steps):
                ang = 2 * math.pi * i / steps
                rad = r + random.randint(-r // 3, r // 3)
                px = int(x + math.cos(ang) * rad)
                py = int(y + math.sin(ang) * rad)
                points.append((px, py))
            pygame.draw.polygon(self.surface, (80, 80, 80), points)
            pygame.draw.polygon(self.collision_surface, (255, 255, 255), points)
            rect = pygame.Rect(x - r, y - r, r * 2, r * 2)
            for i in range(rect.left // self.cell, rect.right // self.cell + 1):
                for j in range(rect.top // self.cell, rect.bottom // self.cell + 1):
                    if 0 <= i < self.cols and 0 <= j < self.rows:
                        self.blocked[j][i] = True
            if random.random() < 0.3:
                self.pickups.append(ItemPickup(random.choice(minerals), x, y))
            if random.random() < 0.5:
                cave_entries.append((x, y))
        if cave_entries:
            self._generate_caves(cave_entries)

    def _generate_caves(self, entries: list[tuple[int, int]]) -> None:
        """Carve simple tunnel networks starting from given entrance points."""
        minerals = ["platino", "diamante", "iridio", "uranio", "palladium"]
        for ex, ey in entries:
            self._carve_circle(ex, ey, 15)
            branch_points = [(ex, ey)]
            for _ in range(random.randint(2, 4)):
                if not branch_points:
                    break
                bx, by = branch_points.pop(0)
                angle = random.uniform(0, 2 * math.pi)
                length = random.randint(80, 160)
                nx = bx + math.cos(angle) * length
                ny = by + math.sin(angle) * length
                self._carve_tunnel(bx, by, nx, ny, 12)
                if random.random() < 0.5:
                    branch_points.append((nx, ny))
                if random.random() < 0.4:
                    self.pickups.append(
                        ItemPickup(random.choice(minerals), int(nx), int(ny))
                    )
                if random.random() < 0.3:
                    self.creatures.append(
                        Creature(int(nx), int(ny), self.width, self.height, hostile=True)
                    )

    def _carve_circle(self, x: float, y: float, radius: int) -> None:
        """Remove collision in a circular region."""
        pygame.draw.circle(self.surface, (50, 50, 50), (int(x), int(y)), radius)
        pygame.draw.circle(self.collision_surface, (0, 0, 0, 0), (int(x), int(y)), radius)
        rect = pygame.Rect(int(x - radius), int(y - radius), radius * 2, radius * 2)
        for i in range(rect.left // self.cell, rect.right // self.cell + 1):
            for j in range(rect.top // self.cell, rect.bottom // self.cell + 1):
                if 0 <= i < self.cols and 0 <= j < self.rows:
                    self.blocked[j][i] = False

    def _carve_tunnel(self, x1: float, y1: float, x2: float, y2: float, radius: int) -> None:
        """Draw a tunnel between two points clearing collisions."""
        steps = int(max(abs(x2 - x1), abs(y2 - y1)) // 8)
        for i in range(steps + 1):
            t = i / steps
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            self._carve_circle(x, y, radius)

    def _draw_mountains(self) -> None:
        """Draw mountain ranges that block movement on the grid."""
        num_ranges = random.randint(2, 4)
        for _ in range(num_ranges):
            width = random.randint(60, 100)
            segs = random.randint(4, 7)
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            angle = random.uniform(0, 2 * math.pi)
            points = [(int(x), int(y))]
            for _ in range(segs):
                step = random.randint(80, 120)
                x += step * math.cos(angle) + random.randint(-30, 30)
                y += step * math.sin(angle) + random.randint(-30, 30)
                angle += random.uniform(-0.4, 0.4)
                points.append((int(x), int(y)))
            pygame.draw.lines(self.surface, (120, 120, 120), False, points, width)
            pygame.draw.lines(self.collision_surface, (255, 255, 255), False, points, width)
            min_x = min(p[0] for p in points) - width // 2
            max_x = max(p[0] for p in points) + width // 2
            min_y = min(p[1] for p in points) - width // 2
            max_y = max(p[1] for p in points) + width // 2
            for i in range(min_x // self.cell, max_x // self.cell + 1):
                for j in range(min_y // self.cell, max_y // self.cell + 1):
                    if 0 <= i < self.cols and 0 <= j < self.rows:
                        self.blocked[j][i] = True

    def _draw_storms(self) -> None:
        """Overlay semi-transparent storm clouds that slow movement."""
        num = random.randint(5, 10)
        for _ in range(num):
            w = random.randint(200, 400)
            h = random.randint(150, 300)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.ellipse(self.storm_surface, config.STORM_COLOR, rect)

    def _spawn_platforms(self) -> None:
        """Create small floating platforms containing optional items."""
        num = random.randint(3, 6)
        for _ in range(num):
            r = random.randint(20, 40)
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - r)
            pygame.draw.circle(self.surface, (190, 190, 190), (x, y), r)
            self.platforms.append(FloatingPlatform(x, y, r))

    def _draw_gas_clouds(self) -> None:
        """Overlay poisonous clouds for toxic planets."""
        num = random.randint(5, 10)
        for _ in range(num):
            w = random.randint(150, 300)
            h = random.randint(120, 240)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.ellipse(self.gas_surface, config.TOXIC_GAS_COLOR, rect)

    def _spawn_waste_deposits(self) -> None:
        """Place hazardous waste that damages when collected."""
        num = random.randint(4, 8)
        for _ in range(num):
            r = random.randint(12, 20)
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - r)
            self.waste_deposits.append(WasteDeposit(x, y, r))

    def _spawn_unique_plants(self) -> None:
        """Scatter healing plants and luminous flowers around the map."""
        for _ in range(random.randint(4, 8)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.healing_plants.append(HealingPlant(x, y))
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.pickups.append(ItemPickup("flor luminosa", x, y))

    def _spawn_creatures(self) -> None:
        """Create a few passive and hostile creatures."""
        num = random.randint(5, 10)
        for _ in range(num):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            hostile = random.random() < 0.5
            self.creatures.append(
                Creature(x, y, self.width, self.height, hostile=hostile)
            )

    def _spawn_underwater_creatures(self) -> None:
        """Populate ocean planets with additional aquatic creatures."""
        count = random.randint(4, 8)
        for _ in range(count):
            for _ in range(100):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.is_water(x, y):
                    hostile = random.random() < 0.5
                    creature = Creature(x, y, self.width, self.height, hostile=hostile)
                    creature.color = (80, 120, 200) if hostile else (60, 180, 190)
                    self.creatures.append(creature)
                    break

    def _draw_islands(self) -> None:
        """Overlay irregular land masses on an ocean planet."""
        num = random.randint(4, 7)
        land_color = ENV_COLORS.get("rocky", (120, 120, 80))
        for _ in range(num):
            r = random.randint(80, 160)
            cx = random.randint(r, self.width - r)
            cy = random.randint(r, self.height - r)
            steps = random.randint(5, 8)
            pts: list[tuple[int, int]] = []
            for i in range(steps):
                ang = 2 * math.pi * i / steps
                rad = r + random.randint(-r // 3, r // 3)
                pts.append((int(cx + math.cos(ang) * rad), int(cy + math.sin(ang) * rad)))
            pygame.draw.polygon(self.surface, land_color, pts)
            pygame.draw.polygon(self.collision_surface, (0, 0, 0, 0), pts)
            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            max_y = max(p[1] for p in pts)
            for i in range(min_x // self.cell, max_x // self.cell + 1):
                for j in range(min_y // self.cell, max_y // self.cell + 1):
                    if 0 <= i < self.cols and 0 <= j < self.rows:
                        cx_cell = i * self.cell + self.cell // 2
                        cy_cell = j * self.cell + self.cell // 2
                        if self._point_in_polygon(cx_cell, cy_cell, pts):
                            self.blocked[j][i] = False

    def _draw_underwater_biomes(self) -> None:
        """Create colourful patches representing underwater biomes."""
        num = random.randint(4, 8)
        for _ in range(num):
            w = random.randint(80, 160)
            h = random.randint(60, 120)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            cx = x + w // 2
            cy = y + h // 2
            if not self.blocked[cy // self.cell][cx // self.cell]:
                continue
            biome = random.choice([BIOMES["coral reef"], BIOMES["deep sea"]])
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.ellipse(self.surface, biome.color, rect)
            for _ in range(random.randint(1, 3)):
                if random.random() < biome.spawn_rate:
                    px = random.randint(rect.left, rect.right)
                    py = random.randint(rect.top, rect.bottom)
                    self.pickups.append(ItemPickup(random.choice(biome.spawn_items), px, py))

    def _spawn_underwater_pickups(self) -> None:
        """Place special collectibles in blocked water cells."""
        items = ["perla abisal", "coral brillante"]
        num = random.randint(10, 20)
        for _ in range(num):
            for _ in range(100):
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                cx = x // self.cell
                cy = y // self.cell
                if 0 <= cx < self.cols and 0 <= cy < self.rows and self.blocked[cy][cx]:
                    self.pickups.append(ItemPickup(random.choice(items), x, y))
                    break

    def _spawn_lava_geysers(self) -> None:
        """Create lava geysers that erupt periodically."""
        count = random.randint(3, 6)
        for _ in range(count):
            r = random.randint(20, 30)
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - r)
            self.lava_geysers.append(
                {
                    "x": x,
                    "y": y,
                    "radius": r,
                    "timer": random.uniform(
                        config.LAVA_GEYSER_INTERVAL_MIN, config.LAVA_GEYSER_INTERVAL_MAX
                    ),
                    "erupt": False,
                }
            )

    def _update_lava_geysers(self, dt: float) -> None:
        """Advance timers, erupt geysers and apply damage."""
        self.lava_surface.fill((0, 0, 0, 0))
        for geyser in self.lava_geysers:
            geyser["timer"] -= dt
            if geyser["erupt"]:
                if geyser["timer"] <= 0:
                    geyser["erupt"] = False
                    geyser["timer"] = random.uniform(
                        config.LAVA_GEYSER_INTERVAL_MIN, config.LAVA_GEYSER_INTERVAL_MAX
                    )
                else:
                    pygame.draw.circle(
                        self.lava_surface,
                        (200, 60, 60, 180),
                        (geyser["x"], geyser["y"]),
                        int(geyser["radius"] * 1.5),
                    )
                    if (
                        math.hypot(self.explorer.x - geyser["x"], self.explorer.y - geyser["y"])
                        < geyser["radius"] * 1.5
                    ):
                        self.explorer.take_damage(config.LAVA_GEYSER_DAMAGE * dt)
            else:
                if geyser["timer"] <= 0:
                    geyser["erupt"] = True
                    geyser["timer"] = config.LAVA_GEYSER_DURATION

    def _draw_ice_fields(self) -> None:
        """Overlay semi-transparent ice zones that affect movement."""
        num = random.randint(4, 8)
        for _ in range(num):
            w = random.randint(120, 250)
            h = random.randint(100, 200)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.ellipse(self.ice_surface, config.ICE_COLOR, rect)

    def _draw_ice_caves(self) -> None:
        """Place cave entrances on the map with energy crystals inside."""
        num = random.randint(3, 6)
        for _ in range(num):
            r = random.randint(20, 40)
            x = random.randint(r, self.width - r)
            y = random.randint(r, self.height - r)
            rect = pygame.Rect(x - r, y - r // 2, r * 2, r)
            pygame.draw.ellipse(self.surface, (140, 150, 160), rect)
            self.pickups.append(ItemPickup("cristal de energia", x, y))

    def _draw_ruins(self) -> None:
        """Scatter small ruins containing valuable items."""
        num = random.randint(3, 6)
        for _ in range(num):
            w = random.randint(60, 120)
            h = random.randint(60, 120)
            x = random.randint(0, self.width - w)
            y = random.randint(0, self.height - h)
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(self.surface, (100, 90, 60), rect, 2)
            pygame.draw.rect(self.collision_surface, (255, 255, 255), rect, 2)
            self.pickups.append(ItemPickup("cofre antiguo", x + w // 2, y + h // 2))

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

        if is_ocean_planet:
            self._draw_islands()
            self._draw_underwater_biomes()
            self._spawn_underwater_pickups()

        for _ in range(random.randint(1, 3)):
            if self.planet.environment == "lava":
                self._draw_river(color=(180, 40, 40), damage=True)
            else:
                self._draw_river()
        forest_range = (2, 4)
        extra_dense = False
        if self.planet.environment == "forest":
            forest_range = (4, 7)
            extra_dense = True
        for _ in range(random.randint(*forest_range)):
            self._draw_forest(extra_dense)

        if self.planet.environment == "rocky":
            self._draw_crater_field()
            self._draw_mountains()
        if self.planet.environment == "desert":
            self._draw_ruins()
        if self.planet.environment == "ice world":
            self._draw_ice_fields()
            self._draw_ice_caves()
        if self.planet.environment == "gas giant":
            self._draw_storms()
            self._spawn_platforms()
        if self.planet.environment == "toxic":
            self._draw_gas_clouds()
            self._spawn_waste_deposits()

        if self.storm_surface.get_width():
            self.storm_mask = pygame.mask.from_surface(self.storm_surface)

        if self.ice_surface.get_width():
            self.ice_mask = pygame.mask.from_surface(self.ice_surface)

        if self.lava_surface.get_width():
            self.lava_mask = pygame.mask.from_surface(self.lava_surface)
        if self.gas_surface.get_width():
            self.gas_mask = pygame.mask.from_surface(self.gas_surface)

        self.collision_mask = pygame.mask.from_surface(self.collision_surface)

    def is_walkable(self, x: float, y: float) -> bool:
        """Return ``True`` if the coordinates correspond to a walkable cell."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        if self.collision_mask and self.collision_mask.get_at((ix, iy)):
            if self.boat_active:
                return True
            if self.player.inventory.get("traje de buceo", 0) > 0:
                return True
            return False
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

    def is_in_storm(self, x: float, y: float) -> bool:
        """Return ``True`` if ``(x, y)`` falls inside a storm zone."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        return bool(self.storm_mask and self.storm_mask.get_at((ix, iy)))

    def is_on_ice(self, x: float, y: float) -> bool:
        """Return ``True`` if ``(x, y)`` lies within an icy area."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        return bool(self.ice_mask and self.ice_mask.get_at((ix, iy)))

    def is_in_lava(self, x: float, y: float) -> bool:
        """Return ``True`` if ``(x, y)`` falls within a lava zone."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        return bool(self.lava_mask and self.lava_mask.get_at((ix, iy)))

    def is_in_gas(self, x: float, y: float) -> bool:
        """Return ``True`` if ``(x, y)`` lies inside a toxic cloud."""
        ix = int(x)
        iy = int(y)
        if not (0 <= ix < self.width and 0 <= iy < self.height):
            return False
        return bool(self.gas_mask and self.gas_mask.get_at((ix, iy)))

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
        wind_dx = 0.0
        if (
            self.planet.environment == "gas giant"
            and self.is_in_storm(self.explorer.x, self.explorer.y)
        ):
            wind_dx = config.STORM_WIND_STRENGTH * dt
        on_water = self.is_water(self.explorer.x, self.explorer.y)
        if self.boat_active:
            if on_water:
                speed = config.BOAT_SPEED_WATER
            else:
                speed = config.BOAT_SPEED_LAND
            if self.boat:
                self.boat.x = self.explorer.x
                self.boat.y = self.explorer.y
        if self.is_in_storm(self.explorer.x, self.explorer.y):
            speed *= config.STORM_SLOW_FACTOR
        if self.is_on_ice(self.explorer.x, self.explorer.y):
            speed *= config.ICE_SLOW_FACTOR
        if self.planet.environment == "lava":
            self._update_lava_geysers(dt)
            if self.is_in_lava(self.explorer.x, self.explorer.y):
                self.explorer.take_damage(config.LAVA_DAMAGE_RATE * dt)
        if self.planet.environment == "desert":
            if self.desert_storm_active:
                self.desert_storm_time -= dt
                if self.desert_storm_time <= 0:
                    self.desert_storm_active = False
                    self.desert_surface.fill((0, 0, 0, 0))
                    self.desert_storm_cooldown = random.uniform(
                        config.DESERT_STORM_INTERVAL_MIN,
                        config.DESERT_STORM_INTERVAL_MAX,
                    )
            else:
                self.desert_storm_cooldown -= dt
                if self.desert_storm_cooldown <= 0:
                    self.desert_storm_active = True
                    self.desert_storm_time = random.uniform(
                        config.DESERT_STORM_MIN_TIME,
                        config.DESERT_STORM_MAX_TIME,
                    )
                    self.desert_surface.fill(config.DESERT_FILTER_COLOR)
        in_gas = False
        has_suit = self.player.inventory.get("traje aislante", 0) > 0
        if self.planet.environment == "toxic":
            in_gas = self.is_in_gas(self.explorer.x, self.explorer.y)
        self.explorer.update(keys, dt, self.width, self.height, speed, in_gas, has_suit)
        if not self.is_walkable(self.explorer.x, self.explorer.y):
            self.explorer.x, self.explorer.y = old_x, old_y
        if wind_dx:
            new_x = max(0, min(self.width - 1, self.explorer.x + wind_dx))
            if self.is_walkable(new_x, self.explorer.y):
                self.explorer.x = new_x
            if self.boat_active and self.boat:
                self.boat.x = self.explorer.x
            for platform in self.platforms:
                if self.is_in_storm(platform.x, platform.y):
                    platform.x = max(
                        platform.radius,
                        min(self.width - platform.radius, platform.x + wind_dx),
                    )
        self.camera_x = self.explorer.x
        self.camera_y = self.explorer.y
        for creature in self.creatures:
            creature.update(self.explorer.x, self.explorer.y, dt)
            if creature.hostile and math.hypot(
                creature.x - self.explorer.x, creature.y - self.explorer.y
            ) < creature.size + self.explorer.size:
                self.explorer.take_damage(20 * dt)
        for plant in self.healing_plants[:]:
            if math.hypot(
                plant.x - self.explorer.x, plant.y - self.explorer.y
            ) < plant.radius + self.explorer.size:
                plant.interact(self.explorer)
                self.healing_plants.remove(plant)
        for pickup in self.pickups[:]:
            if (
                abs(self.explorer.x - pickup.x) < 10
                and abs(self.explorer.y - pickup.y) < 10
            ):
                self.player.add_item(pickup.name)
                self.pickups.remove(pickup)
        for deposit in self.waste_deposits[:]:
            if math.hypot(self.explorer.x - deposit.x, self.explorer.y - deposit.y) < deposit.radius + self.explorer.size:
                self.player.add_item("residuo toxico")
                self.explorer.take_damage(config.RESIDUE_EXTRACTION_DAMAGE)
                self.waste_deposits.remove(deposit)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        offset_x = self.camera_x - config.WINDOW_WIDTH / 2
        offset_y = self.camera_y - config.WINDOW_HEIGHT / 2
        screen.blit(self.surface, (-offset_x, -offset_y))
        screen.blit(self.storm_surface, (-offset_x, -offset_y))
        screen.blit(self.ice_surface, (-offset_x, -offset_y))
        screen.blit(self.lava_surface, (-offset_x, -offset_y))
        screen.blit(self.gas_surface, (-offset_x, -offset_y))
        for platform in self.platforms:
            platform.draw(screen, offset_x, offset_y)
        for plant in self.healing_plants:
            plant.draw(screen, offset_x, offset_y)
        for deposit in self.waste_deposits:
            deposit.draw(screen, offset_x, offset_y)
        for creature in self.creatures:
            creature.draw(screen, offset_x, offset_y)
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
        if self.desert_storm_active:
            screen.blit(self.desert_surface, (-offset_x, -offset_y))
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
