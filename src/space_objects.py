import pygame
import random

# Screen dimensions
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black

class Star:
    """Represents a star in the star system."""
    def __init__(self, x, y, radius, color=(255, 255, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Planet:
    """Represents a planet orbiting a star."""
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class Asteroid:
    """Represents a simple asteroid."""
    def __init__(self, x, y, radius, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

class StarSystem:
    """Procedurally generated collection of a star, planets and asteroids."""
    def __init__(self, width, height):
        self.star = Star(
            random.randint(width // 4, 3 * width // 4),
            random.randint(height // 4, 3 * height // 4),
            random.randint(15, 30)
        )
        self.planets = [
            Planet(
                random.randint(0, width),
                random.randint(0, height),
                random.randint(5, 12),
                (
                    random.randint(50, 255),
                    random.randint(50, 255),
                    random.randint(50, 255)
                )
            )
            for _ in range(random.randint(2, 5))
        ]
        self.asteroids = [
            Asteroid(
                random.randint(0, width),
                random.randint(0, height),
                random.randint(2, 5)
            )
            for _ in range(random.randint(20, 40))
        ]

    def draw(self, screen):
        self.star.draw(screen)
        for planet in self.planets:
            planet.draw(screen)
        for asteroid in self.asteroids:
            asteroid.draw(screen)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Procedural Star System")

    star_system = StarSystem(WINDOW_WIDTH, WINDOW_HEIGHT)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(BACKGROUND_COLOR)
        star_system.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
