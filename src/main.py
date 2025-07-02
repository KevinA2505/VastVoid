import pygame
import config
from ship import Ship
from sector import create_sectors


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")

    sectors = create_sectors(config.GRID_SIZE, config.SECTOR_WIDTH, config.SECTOR_HEIGHT)
    world_width = config.GRID_SIZE * config.SECTOR_WIDTH
    world_height = config.GRID_SIZE * config.SECTOR_HEIGHT
    ship = Ship(world_width // 2, world_height // 2)

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        ship.update(keys, dt, world_width, world_height, sectors)
        for sector in sectors:
            sector.update()

        screen.fill(config.BACKGROUND_COLOR)
        offset_x = ship.x - config.WINDOW_WIDTH // 2
        offset_y = ship.y - config.WINDOW_HEIGHT // 2
        for sector in sectors:
            sector.draw(screen, offset_x, offset_y)
        ship.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()