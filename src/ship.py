import pygame
import math
import config

class Ship:
    """Simple controllable ship."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.autopilot_target = None
        self.boost_charge = 1.0
        self.boost_time = 0.0

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
        accel = config.SHIP_ACCELERATION
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

    @property
    def boost_ratio(self) -> float:
        """Return current boost charge as a 0-1 ratio."""
        if self.boost_time > 0:
            return 0.0
        return self.boost_charge
