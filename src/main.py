import pygame
import config
from ship import Ship
from sector import create_sectors
from star import Star
from planet import Planet


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
    selected_object = None
    info_font = pygame.font.Font(None, 20)

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
                elif event.key == pygame.K_ESCAPE:
                    selected_object = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                offset_x = ship.x - config.WINDOW_WIDTH / (2 * zoom)
                offset_y = ship.y - config.WINDOW_HEIGHT / (2 * zoom)
                world_x = event.pos[0] / zoom + offset_x
                world_y = event.pos[1] / zoom + offset_y
                if event.button == 1:
                    selected_object = None
                    for sector in sectors:
                        obj = sector.get_object_at_point(world_x, world_y, 0)
                        if obj:
                            selected_object = obj
                            break
                elif event.button == 3:
                    selected_object = None

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

        if selected_object:
            panel_width, panel_height = 180, 70
            panel_rect = pygame.Rect(
                config.WINDOW_WIDTH - panel_width - 10,
                10,
                panel_width,
                panel_height,
            )
            pygame.draw.rect(screen, (30, 30, 60), panel_rect)
            pygame.draw.rect(screen, (200, 200, 200), panel_rect, 1)

            if isinstance(selected_object, Star):
                lines = [
                    f"Name: {selected_object.name}",
                    f"Type: Star ({selected_object.spectral_type})",
                    f"Radius: {selected_object.radius}",
                    f"Brightness: {selected_object.brightness}",
                ]
            else:
                lines = [
                    f"Name: {selected_object.name}",
                    "Type: Planet",
                    f"Environment: {selected_object.environment}",
                    f"Radius: {selected_object.radius}",
                ]
            for i, line in enumerate(lines):
                text_surf = info_font.render(line, True, (255, 255, 255))
                screen.blit(text_surf, (panel_rect.x + 5, panel_rect.y + 5 + i * 20))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
