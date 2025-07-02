import pygame
import math
from dataclasses import dataclass
import config
from planet import Planet
from names import get_ship_name
from combat import Weapon, Projectile, Shield


@dataclass
class ShipModel:
    """Template describing a type of ship."""

    classification: str
    brand: str
    size: int
    color: tuple[int, int, int]
    accel_factor: float = 1.0


# Some predefined ship models used during character creation
SHIP_MODELS = [
    ShipModel("Fighter", "AeroTech", 18, (200, 200, 255), 1.2),
    ShipModel("Explorer", "NovaCorp", 20, (255, 220, 150), 1.0),
    ShipModel("Freighter", "Galactic Haul", 24, (180, 180, 180), 0.8),
    ShipModel("Interceptor", "Starlight", 16, (255, 100, 100), 1.4),
]

class Ship:
    """Simple controllable ship with optional model attributes."""

    def __init__(self, x: float, y: float, model: ShipModel | None = None) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.autopilot_target = None
        self.boost_charge = 1.0
        self.boost_time = 0.0
        self.model = model
        self.name = get_ship_name()
        self.weapons: list[Weapon] = [Weapon("Laser", 10, 400)]
        self.projectiles: list[Projectile] = []
        self.shield = Shield()
        self.hull = 100
        if model:
            self.brand = model.brand
            self.classification = model.classification
            self.size = model.size
            self.color = model.color
            self.accel_factor = model.accel_factor
        else:
            self.brand = "Generic"
            self.classification = "Standard"
            self.size = config.SHIP_SIZE
            self.color = config.SHIP_COLOR
            self.accel_factor = 1.0

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
    ) -> None:
        if self.autopilot_target:
            self._update_autopilot(dt, world_width, world_height, sectors, blackholes)
            return
        accel = config.SHIP_ACCELERATION * self.accel_factor
        self.shield.recharge(dt)
        for weapon in self.weapons:
            weapon.update(dt)
        if self.boost_time > 0:
            self.boost_time -= dt
            if self.boost_time <= 0:
                self.boost_time = 0
        else:
            if self.boost_charge < 1.0:
                self.boost_charge = min(1.0, self.boost_charge + dt / config.BOOST_RECHARGE)
            if keys[pygame.K_LSHIFT] and self.boost_charge >= 1.0:
                self.boost_time = config.BOOST_DURATION
                self.boost_charge = 0.0
        if self.boost_time > 0:
            accel *= config.BOOST_MULTIPLIER

        if keys[pygame.K_w]:
            self.vy -= accel * dt
        if keys[pygame.K_s]:
            self.vy += accel * dt
        if keys[pygame.K_a]:
            self.vx -= accel * dt
        if keys[pygame.K_d]:
            self.vx += accel * dt

        self.vx *= config.SHIP_FRICTION
        self.vy *= config.SHIP_FRICTION

        if blackholes:
            for hole in blackholes:
                hole.apply_pull(self, dt)

        old_x, old_y = self.x, self.y

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))

        if self._check_collision(sectors):
            self.x, self.y = old_x, old_y
            self.vx = 0
            self.vy = 0

        self._update_projectiles(dt, world_width, world_height)

    def start_autopilot(self, target) -> None:
        self.autopilot_target = target

    def cancel_autopilot(self) -> None:
        self.autopilot_target = None

    def _update_autopilot(
        self,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
    ) -> None:
        dest_x, dest_y = self.autopilot_target.x, self.autopilot_target.y
        dx = dest_x - self.x
        dy = dest_y - self.y
        distance = math.hypot(dx, dy)
        step = config.AUTOPILOT_SPEED * dt
        if isinstance(self.autopilot_target, Planet):
            step = config.PLANET_LANDING_SPEED * dt
        if distance <= step:
            self.x = dest_x
            self.y = dest_y
            self.autopilot_target = None
            self.vx = 0
            self.vy = 0
            return
        old_x, old_y = self.x, self.y
        self.x += dx / distance * step
        self.y += dy / distance * step
        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))

        if blackholes:
            for hole in blackholes:
                hole.apply_pull(self, dt)
                self.x += self.vx * dt
                self.y += self.vy * dt

        if self._check_collision(sectors):
            self.x, self.y = old_x, old_y
            self.autopilot_target = None

        self._update_projectiles(dt, world_width, world_height)

    def _check_collision(self, sectors: list) -> bool:
        half_size = self.size / 2
        for sector in sectors:
            if sector.collides_with_point(self.x, self.y, half_size):
                return True
        return False

    def draw(self, screen: pygame.Surface, zoom: float = 1.0) -> None:
        """Draw the ship scaled by a non-linear factor of the zoom level."""
        size = max(1, int(self.size * zoom ** 0.5))
        ship_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - size // 2,
            config.WINDOW_HEIGHT // 2 - size // 2,
            size,
            size,
        )
        pygame.draw.rect(screen, self.color, ship_rect)

    @property
    def boost_ratio(self) -> float:
        """Return current boost charge as a 0-1 ratio."""
        if self.boost_time > 0:
            return 0.0
        return self.boost_charge

    def fire(self, tx: float, ty: float) -> None:
        if not self.weapons:
            return
        proj = self.weapons[0].fire(self.x, self.y, tx, ty)
        if proj:
            self.projectiles.append(proj)

    def _update_projectiles(self, dt: float, world_width: int, world_height: int) -> None:
        for proj in list(self.projectiles):
            proj.update(dt)
            if not (0 <= proj.x <= world_width and 0 <= proj.y <= world_height):
                self.projectiles.remove(proj)

    def draw_projectiles(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        for proj in self.projectiles:
            proj.draw(screen, offset_x, offset_y, zoom)

    def draw_at(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        """Draw the ship on screen applying an offset and zoom."""
        size = max(1, int(self.size * zoom ** 0.5))
        ship_rect = pygame.Rect(
            int((self.x - offset_x) * zoom) - size // 2,
            int((self.y - offset_y) * zoom) - size // 2,
            size,
            size,
        )
        pygame.draw.rect(screen, self.color, ship_rect)


def choose_ship(screen: pygame.Surface) -> ShipModel:
    """Let the player select a ship model and return it."""
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.unicode.isdigit():
                idx = int(event.unicode) - 1
                if 0 <= idx < len(SHIP_MODELS):
                    return SHIP_MODELS[idx]
        screen.fill(config.BACKGROUND_COLOR)
        lines = ["Choose your ship:"]
        for i, model in enumerate(SHIP_MODELS):
            lines.append(
                f"{i+1} - {model.brand} {model.classification}"
            )
        for i, line in enumerate(lines):
            msg = font.render(line, True, (255, 255, 255))
            screen.blit(msg, (50, 100 + i * 30))
        pygame.display.flip()
        clock.tick(30)
