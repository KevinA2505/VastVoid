import pygame
import random
import math

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
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Planet:
    """Represents a planet orbiting a star."""
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Asteroid:
    """Represents a simple asteroid."""
    def __init__(self, x, y, radius, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class MovingStarSystem:
    """A star system that moves and can collide with others."""
    def __init__(self, width, height):
        self.star = Star(
            random.randint(width // 4, 3 * width // 4),
            random.randint(height // 4, 3 * height // 4),
            random.randint(15, 30)
        )
        self.planets = [
            Planet(
                self.star.x + random.randint(-40, 40),
                self.star.y + random.randint(-40, 40),
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
                self.star.x + random.randint(-60, 60),
                self.star.y + random.randint(-60, 60),
                random.randint(2, 5)
            )
            for _ in range(random.randint(10, 20))
        ]
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)

    def update(self, width, height):
        self.star.x += self.vx
        self.star.y += self.vy
        for obj in self.planets + self.asteroids:
            obj.x += self.vx
            obj.y += self.vy
        if self.star.x - self.star.radius <= 0 or self.star.x + self.star.radius >= width:
            self.vx *= -1
        if self.star.y - self.star.radius <= 0 or self.star.y + self.star.radius >= height:
            self.vy *= -1

    def draw(self, screen):
        self.star.draw(screen)
        for planet in self.planets:
            planet.draw(screen)
        for asteroid in self.asteroids:
            asteroid.draw(screen)

def check_collision(sys1, sys2):
    dx = sys1.star.x - sys2.star.x
    dy = sys1.star.y - sys2.star.y
    distance = math.hypot(dx, dy)
    if distance < sys1.star.radius + sys2.star.radius:
        sys1.vx, sys2.vx = sys2.vx, sys1.vx
        sys1.vy, sys2.vy = sys2.vy, sys1.vy

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Colliding Star Systems")

    systems = [MovingStarSystem(WINDOW_WIDTH, WINDOW_HEIGHT) for _ in range(3)]
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND_COLOR)

        for i in range(len(systems)):
            for j in range(i + 1, len(systems)):
                check_collision(systems[i], systems[j])

        for system in systems:
            system.update(WINDOW_WIDTH, WINDOW_HEIGHT)
            system.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
