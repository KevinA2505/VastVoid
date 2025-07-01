import pygame
import random
import math

# Screen dimensions
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black
# Ship appearance and movement parameters
SHIP_COLOR = (255, 255, 255)
SHIP_SIZE = 20
SHIP_SPEED = 5  # legacy constant kept for reference
SHIP_ACCELERATION = 300  # pixels per second squared
SHIP_FRICTION = 0.92  # velocity retained each frame
# Base factor used to calculate orbital speed. Lower values mean slower orbits.
ORBIT_SPEED_FACTOR = 0.005

# Sector configuration
SECTOR_WIDTH = 2000
SECTOR_HEIGHT = 2000
GRID_SIZE = 3  # number of sectors per axis

class Star:
    """Represents a star in the star system."""

    def __init__(self, x: float, y: float, radius: int, color=(255, 255, 0)) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        """Draw the star applying an optional camera offset."""
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius,
        )


class Planet:
    """Planet that orbits around a star."""

    def __init__(self, star: Star, distance: float, radius: int, color, angle: float, speed: float) -> None:
        self.star = star
        self.distance = distance
        self.radius = radius
        self.color = color
        self.angle = angle
        self.speed = speed
        self.x = 0.0
        self.y = 0.0
        self.update()

    def update(self) -> None:
        self.angle += self.speed
        self.x = self.star.x + self.distance * math.cos(self.angle)
        self.y = self.star.y + self.distance * math.sin(self.angle)

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.x - offset_x), int(self.y - offset_y)),
            self.radius,
        )


class StarSystem:
    """Collection of a star with orbiting planets."""

    def __init__(self, x, y):
        self.star = Star(x, y, random.randint(15, 30))
        self.planets = []
        num_planets = random.randint(2, 5)
        distances = sorted(random.randint(40, 120) for _ in range(num_planets))
        for distance in distances:
            radius = random.randint(4, 10)
            color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            angle = random.uniform(0, 2 * math.pi)
            # Planets farther away move slower.
            speed = ORBIT_SPEED_FACTOR / math.sqrt(distance)
            self.planets.append(
                Planet(self.star, distance, radius, color, angle, speed)
            )

    def update(self):
        for planet in self.planets:
            planet.update()

    def draw(self, screen: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        self.star.draw(screen, offset_x, offset_y)
        for planet in self.planets:
            planet.draw(screen, offset_x, offset_y)


class Sector:
    """Large region containing multiple star systems."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        num_systems = random.randint(3, 4)
        self.systems = []
        for _ in range(num_systems):
            sx = random.randint(self.x + 100, self.x + self.width - 100)
            sy = random.randint(self.y + 100, self.y + self.height - 100)
            self.systems.append(StarSystem(sx, sy))

    def update(self) -> None:
        for system in self.systems:
            system.update()

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        for system in self.systems:
            system.draw(screen, offset_x, offset_y)


class Ship:
    """Simple controllable ship."""

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def update(self, keys: pygame.key.ScancodeWrapper, dt: float, world_width: int, world_height: int) -> None:
        if keys[pygame.K_w]:
            self.vy -= SHIP_ACCELERATION * dt
        if keys[pygame.K_s]:
            self.vy += SHIP_ACCELERATION * dt
        if keys[pygame.K_a]:
            self.vx -= SHIP_ACCELERATION * dt
        if keys[pygame.K_d]:
            self.vx += SHIP_ACCELERATION * dt

        self.vx *= SHIP_FRICTION
        self.vy *= SHIP_FRICTION

        self.x += self.vx * dt
        self.y += self.vy * dt

        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))

    def draw(self, screen: pygame.Surface) -> None:
        ship_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - SHIP_SIZE // 2,
            WINDOW_HEIGHT // 2 - SHIP_SIZE // 2,
            SHIP_SIZE,
            SHIP_SIZE,
        )
        pygame.draw.rect(screen, SHIP_COLOR, ship_rect)


def create_sectors(grid_size: int) -> list:
    """Generate a grid of sectors filled with random star systems."""
    sectors = []
    for row in range(grid_size):
        for col in range(grid_size):
            x = col * SECTOR_WIDTH
            y = row * SECTOR_HEIGHT
            sectors.append(Sector(x, y, SECTOR_WIDTH, SECTOR_HEIGHT))
    return sectors


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")

    sectors = create_sectors(GRID_SIZE)
    world_width = GRID_SIZE * SECTOR_WIDTH
    world_height = GRID_SIZE * SECTOR_HEIGHT
    ship = Ship(world_width // 2, world_height // 2)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        ship.update(keys, dt, world_width, world_height)
        for sector in sectors:
            sector.update()

        screen.fill(BACKGROUND_COLOR)
        offset_x = ship.x - WINDOW_WIDTH // 2
        offset_y = ship.y - WINDOW_HEIGHT // 2
        for sector in sectors:
            sector.draw(screen, offset_x, offset_y)
        ship.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
