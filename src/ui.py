import pygame
import config
import math

class DropdownMenu:
    """Simple dropdown menu triggered by a button."""

    def __init__(self, x: int, y: int, width: int, height: int, options: list):
        self.button_rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.option_height = height
        self.is_open = False

    def handle_event(self, event) -> str | None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return None
            if self.is_open:
                for i, _ in enumerate(self.options):
                    rect = pygame.Rect(
                        self.button_rect.x,
                        self.button_rect.y + (i + 1) * self.option_height,
                        self.button_rect.width,
                        self.option_height,
                    )
                    if rect.collidepoint(event.pos):
                        self.is_open = False
                        return self.options[i]
                self.is_open = False
        return None

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, (60, 60, 90), self.button_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.button_rect, 1)
        text = font.render("Menu", True, (255, 255, 255))
        screen.blit(text, (self.button_rect.x + 5, self.button_rect.y + 5))
        if self.is_open:
            for i, option in enumerate(self.options):
                rect = pygame.Rect(
                    self.button_rect.x,
                    self.button_rect.y + (i + 1) * self.option_height,
                    self.button_rect.width,
                    self.option_height,
                )
                pygame.draw.rect(screen, (60, 60, 90), rect)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)
                text = font.render(option, True, (255, 255, 255))
                screen.blit(text, (rect.x + 5, rect.y + 5))


class RoutePlanner:
    """Allow selecting a destination and draw a route to it."""

    def __init__(self) -> None:
        self.active = False
        self.destination = None

    def start(self) -> None:
        self.active = True
        self.destination = None

    def cancel(self) -> None:
        self.active = False
        self.destination = None

    def handle_event(self, event, sectors: list, camera_pos, zoom: float) -> None:
        """Process events while selecting a destination."""
        if not self.active:
            return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.cancel()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            offset_x = camera_pos[0] - config.WINDOW_WIDTH / (2 * zoom)
            offset_y = camera_pos[1] - config.WINDOW_HEIGHT / (2 * zoom)
            world_x = event.pos[0] / zoom + offset_x
            world_y = event.pos[1] / zoom + offset_y
            for sector in sectors:
                obj = sector.get_object_at_point(world_x, world_y, 0)
                if obj:
                    self.destination = obj
                    self.active = False
                    break

    def draw(
        self,
        screen: pygame.Surface,
        font: pygame.font.Font,
        ship,
        offset_x: float,
        offset_y: float,
        zoom: float,
    ) -> None:
        if self.destination:
            start = (
                config.WINDOW_WIDTH // 2,
                config.WINDOW_HEIGHT // 2,
            )
            end = (
                int((self.destination.x - offset_x) * zoom),
                int((self.destination.y - offset_y) * zoom),
            )
            pygame.draw.line(screen, (0, 255, 0), start, end, 2)
        if self.active:
            width, height = 200, 50
            rect = pygame.Rect((config.WINDOW_WIDTH - width) // 2, 40, width, height)
            pygame.draw.rect(screen, (30, 30, 60), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            lines = ["Select destination", "Click a planet or star"]
            for i, line in enumerate(lines):
                text = font.render(line, True, (255, 255, 255))
                screen.blit(text, (rect.x + 5, rect.y + 5 + i * 20))


class InventoryWindow:
    """Display the player's inventory and allow using items."""

    def __init__(self, player) -> None:
        self.player = player
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.item_rects: list[tuple[str, pygame.Rect]] = []

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for name, rect in self.item_rects:
                if rect.collidepoint(event.pos):
                    if self.player.inventory.get(name, 0) > 0:
                        self.player.remove_item(name, 1)
                        print(f"Used {name}")
                    return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill((20, 20, 40))
        title = font.render("Inventory", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        self.item_rects.clear()
        x0, y0 = 20, 60
        cell_w, cell_h = 120, 40
        cols = 4
        i = 0
        for name, qty in self.player.inventory.items():
            if qty <= 0:
                continue
            col = i % cols
            row = i // cols
            rect = pygame.Rect(x0 + col * (cell_w + 5), y0 + row * (cell_h + 5), cell_w, cell_h)
            self.item_rects.append((name, rect))
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            txt = font.render(f"{name} ({qty})", True, (255, 255, 255))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
            i += 1
        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        exit_txt = font.render("Close", True, (255, 255, 255))
        exit_rect = exit_txt.get_rect(center=self.close_rect.center)
        screen.blit(exit_txt, exit_rect)


class WeaponMenu:
    """Menu to switch the ship's active weapon."""

    def __init__(self, ship) -> None:
        self.ship = ship
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.weapon_rects: list[tuple[int, pygame.Rect]] = []

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for idx, rect in self.weapon_rects:
                if rect.collidepoint(event.pos):
                    self.ship.set_active_weapon(idx)
                    return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill((20, 20, 40))
        title = font.render("Weapons", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        self.weapon_rects.clear()
        x0, y0 = 20, 60
        w, h = 200, 30
        for i, weapon in enumerate(self.ship.weapons):
            rect = pygame.Rect(x0, y0 + i * (h + 5), w, h)
            self.weapon_rects.append((i, rect))
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            name = weapon.name
            if i == self.ship.active_weapon:
                name = "> " + name
            txt = font.render(name, True, (255, 255, 255))
            txt_rect = txt.get_rect(center=rect.center)
            screen.blit(txt, txt_rect)
        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("Close", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))


class ArtifactMenu:
    """Display the artifacts currently equipped on the ship."""

    def __init__(self, ship) -> None:
        self.ship = ship
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill((20, 20, 40))
        title = font.render("Artifacts", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        x0, y0 = 20, 60
        w, h = 200, 30
        for i, art in enumerate(self.ship.artifacts):
            rect = pygame.Rect(x0, y0 + i * (h + 5), w, h)
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            txt = font.render(art.name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))
        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("Close", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))


class AbilityBar:
    """Display up to five ability slots at the bottom of the screen."""

    SLOT_COUNT = 5
    SLOT_W = 80
    SLOT_H = 40
    MARGIN = 5

    def __init__(self) -> None:
        self.slots: list[tuple[str, str]] = [
            ("Boost", "LShift"),
            ("Orbit", "R"),
            ("", "1"),
            ("", "2"),
            ("", "3"),
        ]
        self.ship = None
        self.rects: list[pygame.Rect] = []
        total_w = self.SLOT_COUNT * (self.SLOT_W + self.MARGIN) - self.MARGIN
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        y = config.WINDOW_HEIGHT - self.SLOT_H - 80
        for i in range(self.SLOT_COUNT):
            rect = pygame.Rect(
                start_x + i * (self.SLOT_W + self.MARGIN), y, self.SLOT_W, self.SLOT_H
            )
            self.rects.append(rect)

    def set_ship(self, ship) -> None:
        self.ship = ship
        self._update_artifact_names()

    def _update_artifact_names(self) -> None:
        for i in range(3):
            name = ""
            if self.ship and i < len(self.ship.artifacts):
                name = self.ship.artifacts[i].name
            self.slots[2 + i] = (name, str(i + 1))

    def handle_event(self, event, ship, enemies: list) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    if idx == 0:
                        if ship.boost_charge >= 1.0:
                            ship.boost_time = config.BOOST_DURATION
                            ship.boost_charge = 0.0
                    elif idx == 1:
                        self._trigger_orbit(ship, enemies)
                    elif idx >= 2:
                        ship.use_artifact(idx - 2, enemies)
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                idx = event.key - pygame.K_1
                ship.use_artifact(idx, enemies)

    def _trigger_orbit(self, ship, enemies: list) -> None:
        nearest = None
        min_dist = float("inf")
        for en in enemies:
            d = math.hypot(en.ship.x - ship.x, en.ship.y - ship.y)
            if d < min_dist:
                min_dist = d
                nearest = en
        if nearest:
            ship.start_orbit(nearest.ship, speed=config.SHIP_ORBIT_SPEED * 0.5)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        for i, rect in enumerate(self.rects):
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            name, key = self.slots[i]
            if name:
                txt = font.render(name, True, (255, 255, 255))
                txt_rect = txt.get_rect(center=(rect.centerx, rect.centery - 8))
                screen.blit(txt, txt_rect)
            key_txt = font.render(key, True, (255, 255, 255))
            key_rect = key_txt.get_rect(bottomright=(rect.right - 4, rect.bottom - 2))
            screen.blit(key_txt, key_rect)

