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

class Star:
    """Represents a star in the star system."""

    def __init__(self, x, y, radius, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


class Planet:
    """Planet that orbits around a star."""

    def __init__(self, star, distance, radius, color, angle, speed):
        self.star = star
        self.distance = distance
        self.radius = radius
        self.color = color
        self.angle = angle
        self.speed = speed
        self.x = 0
        self.y = 0
        self.update()

    def update(self):
        self.angle += self.speed
        self.x = self.star.x + self.distance * math.cos(self.angle)
        self.y = self.star.y + self.distance * math.sin(self.angle)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


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

    def draw(self, screen):
        self.star.draw(screen)
        for planet in self.planets:
            planet.draw(screen)


class Ship:
    """Simple controllable ship."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0

    def update(self, keys, dt):
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

        self.x = max(0, min(WINDOW_WIDTH - SHIP_SIZE, self.x))
        self.y = max(0, min(WINDOW_HEIGHT - SHIP_SIZE, self.y))

    def draw(self, screen):
        pygame.draw.rect(screen, SHIP_COLOR, (int(self.x), int(self.y), SHIP_SIZE, SHIP_SIZE))


def create_star_systems(num_systems):
    systems = []
    for _ in range(num_systems):
        x = random.randint(100, WINDOW_WIDTH - 100)
        y = random.randint(100, WINDOW_HEIGHT - 100)
        systems.append(StarSystem(x, y))
    return systems


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")

    systems = create_star_systems(3)
    ship = Ship(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        ship.update(keys, dt)
        for system in systems:
            system.update()

        screen.fill(BACKGROUND_COLOR)
        for system in systems:
            system.draw(screen)
        ship.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
