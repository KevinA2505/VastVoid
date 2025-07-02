import pygame
import config
from ship import Ship
from sector import create_sectors


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")

    sectors = create_sectors(
        config.GRID_SIZE, config.SECTOR_WIDTH, config.SECTOR_HEIGHT
    )
    world_width = config.GRID_SIZE * config.SECTOR_WIDTH
    world_height = config.GRID_SIZE * config.SECTOR_HEIGHT
    ship = Ship(world_width // 2, world_height // 2)

    zoom = 1.0

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    zoom = max(0.1, zoom - 0.1)
                elif event.key == pygame.K_e:
                    zoom += 0.1

        keys = pygame.key.get_pressed()
        ship.update(keys, dt, world_width, world_height, sectors)
        for sector in sectors:
            sector.update()

        screen.fill(config.BACKGROUND_COLOR)
        offset_x = ship.x - config.WINDOW_WIDTH / (2 * zoom)
        offset_y = ship.y - config.WINDOW_HEIGHT / (2 * zoom)
        for sector in sectors:
            sector.draw(screen, offset_x, offset_y, zoom)
        ship.draw(screen, zoom)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()