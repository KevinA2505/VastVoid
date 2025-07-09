import pygame
import control_settings as controls

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600
BACKGROUND_COLOR = (0, 0, 0)  # black
SHIP_COLOR = (255, 255, 255)  # white
SHIP_SIZE = 20
SPEED = 10

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Nave")

    # Ship starting position in the center
    ship_x = WINDOW_WIDTH // 2
    ship_y = WINDOW_HEIGHT // 2

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[controls.get_key("move_up")]:
            ship_y -= SPEED
        if keys[controls.get_key("move_down")]:
            ship_y += SPEED
        if keys[controls.get_key("move_left")]:
            ship_x -= SPEED
        if keys[controls.get_key("move_right")]:
            ship_x += SPEED

        # Constrain ship to the window boundaries
        ship_x = max(0, min(WINDOW_WIDTH - SHIP_SIZE, ship_x))
        ship_y = max(0, min(WINDOW_HEIGHT - SHIP_SIZE, ship_y))

        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, SHIP_COLOR, (ship_x, ship_y, SHIP_SIZE, SHIP_SIZE))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
