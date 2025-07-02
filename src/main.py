import pygame
import math
import config
from ship import Ship
from sector import create_sectors
from star import Star
from planet import Planet
from ui import DropdownMenu, RoutePlanner


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
    menu = DropdownMenu(10, 10, 100, 25, ["Plan Route"])
    route_planner = RoutePlanner()

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        cancel_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 70, config.WINDOW_HEIGHT - 40, 20, 20
        )
        auto_rect = pygame.Rect(
            cancel_rect.right + 10, config.WINDOW_HEIGHT - 40, 100, 25
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            selection = menu.handle_event(event)
            if selection == "Plan Route":
                route_planner.start()

            route_planner.handle_event(event, sectors, ship, zoom)

            if route_planner.destination:
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and cancel_rect.collidepoint(event.pos)
                ):
                    route_planner.cancel()
                    ship.cancel_autopilot()
                    continue
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and auto_rect.collidepoint(event.pos)
                ):
                    ship.start_autopilot(route_planner.destination)
                    continue

            if event.type == pygame.KEYDOWN:
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
        if (
            route_planner.destination
            and not ship.autopilot_target
            and math.hypot(
                route_planner.destination.x - ship.x,
                route_planner.destination.y - ship.y,
            )
            < 1
        ):
            route_planner.destination = None
        for sector in sectors:
            sector.update()

        screen.fill(config.BACKGROUND_COLOR)
        offset_x = ship.x - config.WINDOW_WIDTH / (2 * zoom)
        offset_y = ship.y - config.WINDOW_HEIGHT / (2 * zoom)
        for sector in sectors:
            sector.draw(screen, offset_x, offset_y, zoom)
        ship.draw(screen, zoom)
        route_planner.draw(screen, info_font, ship, offset_x, offset_y, zoom)

        if selected_object:
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

            panel_width = 180
            line_height = 20
            panel_height = line_height * len(lines) + 10
            panel_rect = pygame.Rect(
                config.WINDOW_WIDTH - panel_width - 10,
                10,
                panel_width,
                panel_height,
            )
            pygame.draw.rect(screen, (30, 30, 60), panel_rect)
            pygame.draw.rect(screen, (200, 200, 200), panel_rect, 1)

            for i, line in enumerate(lines):
                text_surf = info_font.render(line, True, (255, 255, 255))
                screen.blit(
                    text_surf,
                    (panel_rect.x + 5, panel_rect.y + 5 + i * line_height),
                )

        if route_planner.destination:
            pygame.draw.rect(screen, (150, 0, 0), cancel_rect)
            pygame.draw.rect(screen, (200, 200, 200), cancel_rect, 1)
            cancel_text = info_font.render("X", True, (255, 255, 255))
            cancel_rect_text = cancel_text.get_rect(center=cancel_rect.center)
            screen.blit(cancel_text, cancel_rect_text)

            pygame.draw.rect(screen, (60, 60, 90), auto_rect)
            pygame.draw.rect(screen, (200, 200, 200), auto_rect, 1)
            auto_text = info_font.render("Auto Move", True, (255, 255, 255))
            auto_rect_text = auto_text.get_rect(center=auto_rect.center)
            screen.blit(auto_text, auto_rect_text)

        menu.draw(screen, info_font)
        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
