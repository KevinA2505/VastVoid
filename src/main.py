import pygame
import math
import random
import config
from ship import Ship, choose_ship
from carrier import Carrier
from combat import LaserWeapon, MineWeapon, DroneWeapon, MissileWeapon, BasicWeapon
from sector import create_sectors
from fraction import FRACTIONS
from faction_structures import spawn_capital_ships
from portal import Portal
from star import Star
from planet import Planet
from station import SpaceStation
from ui import (
    DropdownMenu,
    RoutePlanner,
    InventoryWindow,
    MarketWindow,
    AbilityBar,
    WeaponMenu,
    ArtifactMenu,
    HyperJumpMap,
    CarrierMoveMap,
    CarrierWindow,
    CrewTransferWindow,
)
from cbm import CommonBerthingMechanism
from artifact import EMPArtifact, AreaShieldArtifact, GravityTractorArtifact
from planet_surface import PlanetSurface
from character import choose_player_table, Robot


class _NullKeys:
    """Object that returns ``False`` for any key lookup."""

    def __getitem__(self, key):
        return False


def _create_vignette(width: int, height: int) -> pygame.Surface:
    """Return a large radial vignette surface."""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    cx, cy = width // 2, height // 2
    max_r = math.hypot(cx, cy)
    step = 4
    for r in range(int(max_r), 0, -step):
        alpha = int(config.HYPERJUMP_VIGNETTE_ALPHA * (r / max_r))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (cx, cy), r)
    return surf

def draw_station_ui(
    screen: pygame.Surface,
    station: SpaceStation,
    font: pygame.font.Font,
    player,
) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
    """Draw a simple interface for a space station and return button rects."""
    screen.fill((20, 20, 40))
    title = font.render(station.name, True, (255, 255, 255))
    screen.blit(title, (20, 20))
    credits_txt = font.render(f"Credits: {player.credits}", True, (255, 255, 255))
    screen.blit(credits_txt, (20, 40))
    y = 80
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

    inv_rect = pygame.Rect(10, 10, 100, 30)
    pygame.draw.rect(screen, (60, 60, 90), inv_rect)
    pygame.draw.rect(screen, (200, 200, 200), inv_rect, 1)
    inv_txt = font.render("Items", True, (255, 255, 255))
    inv_txt_rect = inv_txt.get_rect(center=inv_rect.center)
    screen.blit(inv_txt, inv_txt_rect)
    market_rect = pygame.Rect(10, 50, 100, 30)
    pygame.draw.rect(screen, (60, 60, 90), market_rect)
    pygame.draw.rect(screen, (200, 200, 200), market_rect, 1)
    market_txt = font.render("Market", True, (255, 255, 255))
    market_txt_rect = market_txt.get_rect(center=market_rect.center)
    screen.blit(market_txt, market_txt_rect)
    return exit_rect, inv_rect, market_rect



def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("VastVoid")
    vignette = _create_vignette(config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

    player = choose_player_table(screen)

    sectors = create_sectors(
        config.GRID_SIZE, config.SECTOR_WIDTH, config.SECTOR_HEIGHT
    )
    blackholes = []
    wormholes = []
    for sector in sectors:
        blackholes.extend(sector.blackholes)
        wormholes.extend(sector.wormholes)
    world_width = config.GRID_SIZE * config.SECTOR_WIDTH
    world_height = config.GRID_SIZE * config.SECTOR_HEIGHT

    capital_ships = spawn_capital_ships(FRACTIONS, world_width, world_height)
    free_ship = next((c for c in capital_ships if c.fraction and c.fraction.name == "Free Explorers"), None)
    portals = []
    if free_ship:
        from portal import spawn_explorer_portals
        portals = spawn_explorer_portals(free_ship, world_width, world_height)

    portals: list[Portal] = []
    free_flagship = next(
        (c for c in capital_ships if c.fraction and c.fraction.name == "Free Explorers"),
        None,
    )
    if free_flagship:
        portals = spawn_explorer_portals(free_flagship, world_width, world_height)

    chosen_model = choose_ship(screen)
    player.ship_model = chosen_model
    ship = Ship(
        world_width // 2,
        world_height // 2,
        chosen_model,
        hull=config.PLAYER_MAX_HULL,
        fraction=player.fraction,
        speed_factor=config.NPC_SPEED_FACTOR,
    )
    ship.weapons.extend([
        LaserWeapon(),
        MineWeapon(),
        DroneWeapon(),
        MissileWeapon(),
        BasicWeapon(),
    ])
    for w in ship.weapons:
        w.owner = ship
    ship.artifacts = [EMPArtifact(), AreaShieldArtifact(), GravityTractorArtifact()]

    pepe = Robot()
    pepe.name = "PEPE"
    ship.add_passenger(pepe)

    # Create an additional ship a short distance from the player. It has no
    # crew assigned and simply exists alongside the main player ship.
    extra_npc = Ship(
        ship.x + 350,
        ship.y,
        chosen_model,
        hull=config.PLAYER_MAX_HULL,
        fraction=player.fraction,
        speed_factor=config.NPC_SPEED_FACTOR,
    )

    zoom = 1.0
    selected_object = None
    info_font = pygame.font.Font(None, 20)
    menu = DropdownMenu(10, 10, 100, 25, ["Plan Route", "Inventory", "Weapons", "Artifacts"])
    route_planner = RoutePlanner()
    ability_bar = AbilityBar()
    ability_bar.set_ship(ship)
    carrier = Carrier(ship.x + 150, ship.y + 80, fraction=player.fraction)
    extra_ships = [extra_npc]
    cbm = CommonBerthingMechanism(ship, extra_npc)
    crew_window = None
    inventory_window = None
    market_window = None
    weapon_menu = None
    artifact_menu = None
    carrier_window = None
    current_station = None
    current_surface = None
    approaching_planet = None
    teleport_target = None
    teleport_timer = 0.0
    wormhole_cooldown = 0.0
    portal_cooldown = 0.0
    teleport_flash_timer = 0.0
    blackhole_flash_timer = 0.0
    swallowed = False
    pending_tractor = None
    hyper_map = None
    carrier_move_map = None
    camera_x = ship.x
    camera_y = ship.y
    camera_dragging = False
    camera_last = (0, 0)
    last_pan_time = config.CAMERA_RECENTER_DELAY
    load_mode = False

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        last_pan_time += dt

        if wormhole_cooldown > 0:
            wormhole_cooldown -= dt
        if portal_cooldown > 0:
            portal_cooldown -= dt
        if teleport_flash_timer > 0:
            teleport_flash_timer -= dt
        if blackhole_flash_timer > 0:
            blackhole_flash_timer -= dt

        if teleport_timer > 0:
            teleport_timer -= dt
            if teleport_timer <= 0 and teleport_target:
                ship.x = teleport_target.x
                ship.y = teleport_target.y
                teleport_target = None
                wormhole_cooldown = config.WORMHOLE_COOLDOWN
                teleport_flash_timer = config.WORMHOLE_FLASH_TIME

        # Detect if the player now pilots a different ship and switch control
        active_ship = None
        for candidate in [ship, carrier, *extra_ships, *capital_ships]:
            if getattr(candidate, "pilot", None) is player:
                active_ship = candidate
                break
        if active_ship and active_ship is not ship:
            ship = active_ship
            ability_bar.set_ship(ship)
            if weapon_menu:
                weapon_menu.ship = ship
            if artifact_menu:
                artifact_menu.ship = ship

        if cbm.docked and crew_window is None:
            crew_window = CrewTransferWindow(cbm.ship_a, cbm.ship_b)

        if current_surface:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if inventory_window:
                    if inventory_window.handle_event(event):
                        inventory_window = None
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    inventory_window = InventoryWindow(player)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    weapon_menu = WeaponMenu(ship)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    artifact_menu = ArtifactMenu(ship, ability_bar)
                    continue
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and current_surface.inventory_rect.collidepoint(event.pos)
                ):
                    inventory_window = InventoryWindow(player)
                    continue
                if current_surface.handle_event(event):
                    planet = current_surface.planet
                    current_surface = None
                    ship.x = planet.x + planet.radius + 40
                    ship.y = planet.y
                    camera_x = ship.x
                    camera_y = ship.y
                    break
            if current_surface:
                keys = pygame.key.get_pressed()
                current_surface.update(keys, dt)
                current_surface.draw(screen, info_font)
                if inventory_window:
                    inventory_window.draw(screen, info_font)
                pygame.display.flip()
                continue

        if inventory_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if inventory_window.handle_event(event):
                    inventory_window = None
                    break
            if inventory_window:
                inventory_window.draw(screen, info_font)
                pygame.display.flip()
                continue

        if weapon_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if weapon_menu.handle_event(event):
                    weapon_menu = None
                    break
            if weapon_menu:
                weapon_menu.draw(screen, info_font)
                pygame.display.flip()
                continue

        if artifact_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if artifact_menu.handle_event(event):
                    artifact_menu = None
                    break
            if artifact_menu:
                artifact_menu.draw(screen, info_font)
                pygame.display.flip()
                continue

        if hyper_map:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if hyper_map.handle_event(event):
                    hyper_map = None
                    break
            if hyper_map:
                hyper_map.draw(screen, info_font)
                pygame.display.flip()
                continue

        if carrier_move_map:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if carrier_move_map.handle_event(event):
                    carrier_move_map = None
                    break
            if carrier_move_map:
                carrier_move_map.draw(screen, info_font)
                pygame.display.flip()
                continue

        if carrier_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                closed = carrier_window.handle_event(event)
                if closed:
                    if carrier_window.request_move:
                        move_objects = [ship] + extra_ships + capital_ships
                        carrier_move_map = CarrierMoveMap(
                            carrier,
                            sectors,
                            world_width,
                            world_height,
                            move_objects,
                        )
                        carrier_window.request_move = False
                    carrier_window = None
                    break
                if carrier_window and carrier_window.deployed_ship:
                    extra_ships.append(carrier_window.deployed_ship)
                    carrier_window.deployed_ship = None
            if carrier_window:
                carrier_window.draw(screen, info_font)
                pygame.display.flip()
                continue

        if crew_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if crew_window.handle_event(event):
                    cbm.undock()
                    crew_window = None
                    break
            if crew_window:
                crew_window.draw(screen, info_font)
                pygame.display.flip()
                continue

        if market_window:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if market_window.handle_event(event):
                    market_window = None
                    break
            if market_window:
                market_window.draw(screen, info_font)
                pygame.display.flip()
                continue

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

            if load_mode:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    load_mode = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
                    offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
                    wx = event.pos[0] / zoom + offset_x
                    wy = event.pos[1] / zoom + offset_y
                    target = None
                    for extra in extra_ships:
                        obj = getattr(extra, "ship", extra)
                        if math.hypot(obj.x - wx, obj.y - wy) <= obj.collision_radius:
                            target = extra
                            break
                    if target and carrier.load_ship(getattr(target, "ship", target)):
                        extra_ships.remove(target)
                    load_mode = False
                continue

            if current_station:
                leave_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
                inv_rect = pygame.Rect(10, 10, 100, 30)
                market_rect = pygame.Rect(10, 50, 100, 30)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_station.undock_ship(ship)
                    ship.x = current_station.x + current_station.radius + 40
                    current_station = None
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                    inventory_window = InventoryWindow(player)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    market_window = MarketWindow(current_station, player)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    weapon_menu = WeaponMenu(ship)
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
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and inv_rect.collidepoint(event.pos)
                ):
                    inventory_window = InventoryWindow(player)
                    continue
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and market_rect.collidepoint(event.pos)
                ):
                    market_window = MarketWindow(current_station, player)
                    continue
                continue

            selection = menu.handle_event(event)
            if selection == "Plan Route":
                route_planner.start()
            elif selection == "Inventory":
                inventory_window = InventoryWindow(player)
            elif selection == "Weapons":
                weapon_menu = WeaponMenu(ship)
            elif selection == "Artifacts":
                artifact_menu = ArtifactMenu(ship, ability_bar)

            route_planner.handle_event(event, sectors, (camera_x, camera_y), zoom)
            if ability_bar.handle_event(event, ship):
                map_objects = [carrier] + extra_ships + capital_ships
                hyper_map = HyperJumpMap(
                    ship,
                    sectors,
                    world_width,
                    world_height,
                    map_objects,
                )

            if pending_tractor is None:
                for art in ship.artifacts:
                    if isinstance(art, GravityTractorArtifact) and art.awaiting_click:
                        pending_tractor = art
                        break

            if pending_tractor and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
                offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
                world_x = event.pos[0] / zoom + offset_x
                world_y = event.pos[1] / zoom + offset_y
                pending_tractor.confirm(world_x, world_y)
                pending_tractor = None
                continue

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
                elif event.key == pygame.K_i:
                    inventory_window = InventoryWindow(player)
                elif event.key == pygame.K_f:
                    weapon_menu = WeaponMenu(ship)
                elif event.key == pygame.K_g:
                    artifact_menu = ArtifactMenu(ship, ability_bar)
                elif event.key == pygame.K_l:
                    load_mode = True
                elif event.key == pygame.K_c:
                    cbm.attempt_dock()
                elif event.key == pygame.K_SPACE:
                    mx, my = pygame.mouse.get_pos()
                    offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
                    offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
                    tx = mx / zoom + offset_x
                    ty = my / zoom + offset_y
                    ship.fire(tx, ty)
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
                    if selected_object and isinstance(selected_object, Planet):
                        lines = [
                            f"Name: {selected_object.name}",
                            "Type: Planet",
                            f"Environment: {selected_object.environment}",
                            f"Radius: {selected_object.radius}",
                        ]
                        panel_height = len(lines) * 20 + 10 + 30
                        panel_width = 180
                        panel_rect = pygame.Rect(
                            config.WINDOW_WIDTH - panel_width - 10,
                            10,
                            panel_width,
                            panel_height,
                        )
                        visit_rect = pygame.Rect(
                            panel_rect.x + 10,
                            panel_rect.bottom - 25,
                            panel_rect.width - 20,
                            20,
                        )
                        if visit_rect.collidepoint(event.pos):
                            approaching_planet = selected_object
                            ship.start_autopilot(selected_object)
                            selected_object = None
                            continue
                    selected_object = None
                    for sector in sectors:
                        obj = sector.get_object_at_point(world_x, world_y, 0)
                        if obj:
                            selected_object = obj
                            break
                    if selected_object is None:
                        if math.hypot(carrier.x - world_x, carrier.y - world_y) <= carrier.collision_radius:
                            carrier_window = CarrierWindow(carrier)
                            continue
                elif event.button == 3:
                    camera_dragging = True
                    camera_last = event.pos
                    last_pan_time = 0.0
                    selected_object = None

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                camera_dragging = False
                last_pan_time = 0.0
            elif event.type == pygame.MOUSEMOTION:
                if camera_dragging:
                    dx = event.pos[0] - camera_last[0]
                    dy = event.pos[1] - camera_last[1]
                    camera_x -= dx / zoom
                    camera_y -= dy / zoom
                    camera_last = event.pos
                    last_pan_time = 0.0

        if current_station:
            leave_rect, inv_rect, market_rect = draw_station_ui(
                screen, current_station, info_font, player
            )
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        hostiles = []
        structures = []
        for cap in capital_ships:
            structures.append(cap)
            structures.extend(cap.city_stations)
        structures.append(carrier)

        ship.update(
            keys,
            dt,
            world_width,
            world_height,
            sectors,
            blackholes,
            hostiles,
            structures,
        )
        carrier.update(
            _NullKeys(),
            dt,
            world_width,
            world_height,
            sectors,
            blackholes,
            hostiles,
            structures,
        )
        for extra in extra_ships:
            extra.update(
                _NullKeys(),
                dt,
                world_width,
                world_height,
                sectors,
                blackholes,
                hostiles,
                structures,
            )
        if approaching_planet and not ship.autopilot_target:
            dist = math.hypot(
                approaching_planet.x - ship.x,
                approaching_planet.y - ship.y,
            )
            if dist <= approaching_planet.radius + 20:
                current_surface = PlanetSurface(approaching_planet, player)
                approaching_planet = None
                camera_x = current_surface.camera_x
                camera_y = current_surface.camera_y
            else:
                approaching_planet = None
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
                swallowed = True
                blackhole_flash_timer = config.BLACKHOLE_FLASH_TIME
                break
        if swallowed and blackhole_flash_timer <= 0:
            running = False
        if not running:
            continue

        if teleport_timer <= 0 and wormhole_cooldown <= 0:
            for wh in wormholes:
                if math.hypot(wh.x - ship.x, wh.y - ship.y) < wh.radius:
                    if wh.pair:
                        teleport_target = wh.pair
                        teleport_timer = config.WORMHOLE_DELAY
                        print("Entering wormhole...")
                    break
        if portal_cooldown <= 0:
            for portal in portals:
                if math.hypot(portal.x - ship.x, portal.y - ship.y) < portal.radius:
                    if portal.pair:
                        allowed = player.fraction and player.fraction.name == portal.allowed_faction
                        if not allowed:
                            if player.credits < config.PORTAL_USE_COST:
                                break
                            player.credits -= config.PORTAL_USE_COST
                        ship.x = portal.pair.x
                        ship.y = portal.pair.y
                        portal_cooldown = config.PORTAL_COOLDOWN
                    break
        for sector in sectors:
            sector.update(dt)
        # Update roaming capital ships so their arms can track nearby stars
        for cap in capital_ships:
            # Pass the player's ship so capital ships know the player's
            # faction when determining hostiles and can target it correctly
            cap.update(dt, sectors, [], ship)

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
            if not camera_dragging and last_pan_time >= config.CAMERA_RECENTER_DELAY:
                moving = (
                    ship.autopilot_target is not None
                    or ship.hyperjump_active
                    or abs(ship.vx) > 0.1
                    or abs(ship.vy) > 0.1
                )
                if moving:
                    t = min(1.0, config.CAMERA_RECENTER_SPEED * dt)
                    camera_x += (ship.x - camera_x) * t
                    camera_y += (ship.y - camera_y) * t
            if ship.hyperjump_active:
                camera_x += random.uniform(-5, 5)
                camera_y += random.uniform(-5, 5)
        offset_x = camera_x - config.WINDOW_WIDTH / (2 * zoom)
        offset_y = camera_y - config.WINDOW_HEIGHT / (2 * zoom)
        for sector in sectors:
            sector.draw(screen, offset_x, offset_y, zoom)
        for p in portals:
            p.draw(screen, offset_x, offset_y, zoom)
        for cap in capital_ships:
            cap.draw(screen, offset_x, offset_y, zoom)
        for portal in portals:
            portal.draw(screen, offset_x, offset_y, zoom)
        carrier.draw(
            screen,
            player.fraction,
            offset_x,
            offset_y,
            zoom,
            aura_color=player.fraction.color if player.fraction else None,
        )
        for extra in extra_ships:
            extra_ship = getattr(extra, "ship", extra)
            extra_ship.draw_projectiles(screen, offset_x, offset_y, zoom)
        ship.draw_projectiles(screen, offset_x, offset_y, zoom)
        ship.draw_specials(screen, offset_x, offset_y, zoom)
        for extra in extra_ships:
            extra_ship = getattr(extra, "ship", extra)
            extra_ship.draw_at(
                screen,
                offset_x,
                offset_y,
                zoom,
                player.fraction,
                player.fraction.color if player.fraction else None,
            )
        ship.draw_at(screen, offset_x, offset_y, zoom, player.fraction)
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
            has_visit = isinstance(selected_object, Planet)
            if has_visit:
                panel_height += 30
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
            visit_rect = None
            if has_visit:
                visit_rect = pygame.Rect(
                    panel_rect.x + 10,
                    panel_rect.bottom - 25,
                    panel_rect.width - 20,
                    20,
                )
                pygame.draw.rect(screen, (60, 60, 90), visit_rect)
                pygame.draw.rect(screen, (200, 200, 200), visit_rect, 1)
                icon = info_font.render("\u25B2", True, (255, 255, 255))
                screen.blit(icon, (visit_rect.x + 5, visit_rect.y + 3))
                txt = info_font.render("Visit planet", True, (255, 255, 255))
                # Ensure we reference the correct rectangle for the button text
                txt_rect = txt.get_rect(midleft=(visit_rect.x + 20, visit_rect.centery))
                screen.blit(txt, txt_rect)

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

        shield_y = bar_y - 15
        pygame.draw.rect(screen, (60, 60, 90), (bar_x, shield_y, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, shield_y, bar_width, bar_height), 1)
        shield_fill = int(bar_width * ship.shield.strength / ship.shield.max_strength)
        if shield_fill > 0:
            pygame.draw.rect(screen, (0, 0, 150), (bar_x, shield_y, shield_fill, bar_height))

        hull_y = shield_y - 15
        pygame.draw.rect(screen, (60, 60, 90), (bar_x, hull_y, bar_width, bar_height))
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, hull_y, bar_width, bar_height), 1)
        hull_fill = int(bar_width * ship.hull / config.PLAYER_MAX_HULL)
        if hull_fill > 0:
            pygame.draw.rect(screen, (150, 0, 0), (bar_x, hull_y, hull_fill, bar_height))
        ability_bar.draw(screen, info_font)
        menu.draw(screen, info_font)

        if load_mode:
            txt = info_font.render("Select allied ship to load or ESC", True, (255, 255, 255))
            rect = txt.get_rect(center=(config.WINDOW_WIDTH // 2, 30))
            screen.blit(txt, rect)

        if pending_tractor:
            width, height = 220, 40
            rect = pygame.Rect((config.WINDOW_WIDTH - width) // 2, 40, width, height)
            pygame.draw.rect(screen, (30, 30, 60), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            lines = ["Place Gravity Tractor", "Click a location"]
            for i, line in enumerate(lines):
                txt = info_font.render(line, True, (255, 255, 255))
                screen.blit(txt, (rect.x + 5, rect.y + 5 + i * 20))

        if ship.hyperjump_active:
            screen.blit(vignette, (0, 0))
        if teleport_flash_timer > 0:
            alpha = int(255 * (teleport_flash_timer / config.WORMHOLE_FLASH_TIME))
            flash = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (0, 0))
        if blackhole_flash_timer > 0:
            alpha = int(255 * (blackhole_flash_timer / config.BLACKHOLE_FLASH_TIME))
            flash = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, alpha))
            screen.blit(flash, (0, 0))

        pygame.display.flip()

    # Save learning data so drones retain behavior between sessions
    for extra in extra_ships:
        if hasattr(extra, "save_q_table"):
            extra.save_q_table()

    pygame.quit()


if __name__ == "__main__":
    main()
