import pygame
import math
import config
from ship import Ship
from sector import create_sectors
from star import Star
from planet import Planet
from station import SpaceStation
from ui import DropdownMenu, RoutePlanner
from character import create_player


def draw_station_ui(screen: pygame.Surface, station: SpaceStation, font: pygame.font.Font) -> pygame.Rect:
    """Draw a simple interface for a space station and return the exit button rect."""
    screen.fill((20, 20, 40))
    title = font.render(station.name, True, (255, 255, 255))
    screen.blit(title, (20, 20))
    y = 60
    for i, hangar in enumerate(station.hangars):
        status = "Occupied" if hangar.occupied else "Free"
        text = font.render(f"Hangar {i+1}: {status}", True, (255, 255, 255))
        screen.blit(text, (40, y))
        y += 20
    exit_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
    pygame.draw.rect(screen, (60, 60, 90), exit_rect)
    pygame.draw.rect(screen, (200, 200, 200), exit_rect, 1)
    exit_txt = font.render("Leave", True, (255, 255, 255))
    exit_txt_rect = exit_txt.get_rect(center=exit_rect.center)
    screen.blit(exit_txt, exit_txt_rect)
    return exit_rect


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")

    player = create_player(screen)

    sectors = create_sectors(
        config.GRID_SIZE, config.SECTOR_WIDTH, config.SECTOR_HEIGHT
    )
    blackholes = []
    for sector in sectors:
        blackholes.extend(sector.blackholes)
    world_width = config.GRID_SIZE * config.SECTOR_WIDTH
    world_height = config.GRID_SIZE * config.SECTOR_HEIGHT
    ship = Ship(world_width // 2, world_height // 2)

    zoom = 1.0
    selected_object = None
    info_font = pygame.font.Font(None, 20)
    menu = DropdownMenu(10, 10, 100, 25, ["Plan Route"])
    route_planner = RoutePlanner()
    current_station = None
    camera_x = ship.x
    camera_y = ship.y

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        near_station = None
        if not current_station:
            for sector in sectors:
                for system in sector.systems:
                    for station in system.stations:
                        if math.hypot(station.x - ship.x, station.y - ship.y) < station.radius + 40:
                            near_station = station
                            break
                    if near_station:
                        break
                if near_station:
                    break
        cancel_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 70, config.WINDOW_HEIGHT - 40, 20, 20
        )
        auto_rect = pygame.Rect(
            cancel_rect.right + 10, config.WINDOW_HEIGHT - 40, 100, 25
        )
        enter_rect = pygame.Rect(
            config.WINDOW_WIDTH // 2 - 50, config.WINDOW_HEIGHT - 80, 100, 30
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if current_station:
                leave_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_station.undock_ship(ship)
                    ship.x = current_station.x + current_station.radius + 40
                    current_station = None
                    continue
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and leave_rect.collidepoint(event.pos)
                ):
                    current_station.undock_ship(ship)
                    ship.x = current_station.x + current_station.radius + 40
                    current_station = None
                continue

            selection = menu.handle_event(event)
            if selection == "Plan Route":
                route_planner.start()

            route_planner.handle_event(event, sectors, (camera_x, camera_y), zoom)

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
                offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
                offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
                world_x = event.pos[0] / zoom + offset_x
                world_y = event.pos[1] / zoom + offset_y
                if event.button == 1:
                    if near_station and enter_rect.collidepoint(event.pos):
                        if near_station.dock_ship(ship):
                            current_station = near_station
                        continue
                    selected_object = None
                    for sector in sectors:
                        obj = sector.get_object_at_point(world_x, world_y, 0)
                        if obj:
                            selected_object = obj
                            break
                elif event.button == 3:
                    selected_object = None

        if current_station:
            leave_rect = draw_station_ui(screen, current_station, info_font)
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        ship.update(keys, dt, world_width, world_height, sectors, blackholes)
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

        for hole in blackholes:
            if math.hypot(hole.x - ship.x, hole.y - ship.y) < hole.radius:
                print("You were swallowed by a black hole!")
                running = False
                break
        if not running:
            continue
        for sector in sectors:
            sector.update()

        screen.fill(config.BACKGROUND_COLOR)
        if route_planner.active:
            if keys[pygame.K_LEFT]:
                camera_x -= config.CAMERA_PAN_SPEED * dt
            if keys[pygame.K_RIGHT]:
                camera_x += config.CAMERA_PAN_SPEED * dt
            if keys[pygame.K_UP]:
                camera_y -= config.CAMERA_PAN_SPEED * dt
            if keys[pygame.K_DOWN]:
                camera_y += config.CAMERA_PAN_SPEED * dt
        else:
            camera_x = ship.x
            camera_y = ship.y
        offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
        offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
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
            elif isinstance(selected_object, Planet):
                lines = [
                    f"Name: {selected_object.name}",
                    "Type: Planet",
                    f"Environment: {selected_object.environment}",
                    f"Radius: {selected_object.radius}",
                ]
            else:
                lines = [
                    f"Name: {selected_object.name}",
                    "Type: Station",
                    f"Hangars: {len(selected_object.hangars)}",
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

        if near_station and not current_station:
            pygame.draw.rect(screen, (60, 60, 90), enter_rect)
            pygame.draw.rect(screen, (200, 200, 200), enter_rect, 1)
            enter_text = info_font.render("Enter", True, (255, 255, 255))
            enter_text_rect = enter_text.get_rect(center=enter_rect.center)
            screen.blit(enter_text, enter_text_rect)

        # draw boost bar
        bar_width = 100
        bar_height = 10
        bar_x = (config.WINDOW_WIDTH - bar_width) // 2
        bar_y = config.WINDOW_HEIGHT - 20
        pygame.draw.rect(screen, (60, 60, 90), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 1)
        fill_width = int(bar_width * ship.boost_ratio)
        if fill_width > 0:
            pygame.draw.rect(screen, (0, 150, 0), (bar_x, bar_y, fill_width, bar_height))

        menu.draw(screen, info_font)
        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
