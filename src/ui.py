import pygame
import config
import control_settings as controls
import game_settings as settings
import math
import types
from artifact import Artifact
from combat import LaserWeapon
from tech_tree import ResearchManager
from tech_ui import draw_tree, draw_info, _compute_levels, _layout_nodes

# Default key bindings for common actions. These match the table in the README
# so they can be displayed in the in-game Ajustes/Settings window.
DEFAULT_CONTROLS = [
    ("Mover nave o explorador", "W, A, S, D"),
    ("Impulso (boost)", "Mantener LSHIFT"),
    ("Abrir inventario", "I"),
    ("Abrir menú de armas", "F"),
    ("Abrir menú de artefactos", "G"),
    ("Abrir mercado en estación", "M"),
    ("Iniciar acoplamiento", "C"),
    ("Cargar nave aliada en portador", "L"),
    ("Disparar arma principal", "Barra espaciadora"),
    ("Seleccionar/interactuar o mover nave", "Clic izquierdo"),
    ("Cerrar ventana o cancelar", "Escape"),
    ("Cambiar zoom", "Rueda del ratón"),
    ("Elegir ranura (al equipar)", "1, 2 o 3"),
    ("Mover cámara en planificador", "Flechas del teclado"),
    ("Activar/desactivar bote", "B"),
]

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
                int((ship.x - offset_x) * zoom),
                int((ship.y - offset_y) * zoom),
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


class MarketWindow:
    """Trade items between the player and a station."""

    def __init__(self, station, player) -> None:
        self.station = station
        self.player = player
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.buy_rects: list[tuple[str, pygame.Rect]] = []
        self.sell_rects: list[tuple[str, pygame.Rect]] = []

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for name, rect in self.buy_rects:
                if rect.collidepoint(event.pos):
                    self.station.buy_item(self.player, name, 1)
                    return False
            for name, rect in self.sell_rects:
                if rect.collidepoint(event.pos):
                    self.station.sell_item(self.player, name, 1)
                    return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        from items import ITEMS_BY_NAME

        screen.fill((20, 20, 40))
        title = font.render(f"Market - {self.player.credits} cr", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        self.buy_rects.clear()
        self.sell_rects.clear()
        x0, y0 = 20, 60
        w, h = 200, 30
        for i, (name, qty) in enumerate(self.station.market.items()):
            rect = pygame.Rect(x0, y0 + i * (h + 5), w, h)
            self.buy_rects.append((name, rect))
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            item = ITEMS_BY_NAME[name]
            price = item.valor
            if self.player.fraction.name == "Cosmic Guild":
                price = int(price * 0.9)
            txt = font.render(f"Buy {name} ({qty}) - {price}", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))

        x1 = x0 + w + 40
        sell_items = [(n, q) for n, q in self.player.inventory.items() if q > 0]
        for i, (name, qty) in enumerate(sell_items):
            rect = pygame.Rect(x1, y0 + i * (h + 5), w, h)
            self.sell_rects.append((name, rect))
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            item = ITEMS_BY_NAME[name]
            price = item.valor
            if self.player.fraction.name == "Cosmic Guild":
                price = int(price * 1.1)
            txt = font.render(f"Sell {name} ({qty}) +{price}", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))

        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("Close", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))


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
                    weapon = self.ship.weapons[idx]
                    pilot_feats = (
                        getattr(self.ship.pilot, "features", set())
                        if self.ship.pilot
                        else set()
                    )
                    locked = isinstance(weapon, LaserWeapon) and (
                        "Laser Cannons" not in pilot_feats
                    )
                    if locked:
                        # Weapon is locked; ignore the selection
                        return False
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
            pilot_feats = (
                getattr(self.ship.pilot, "features", set()) if self.ship.pilot else set()
            )
            locked = isinstance(weapon, LaserWeapon) and "Laser Cannons" not in pilot_feats
            if locked:
                name = "(Locked) " + name
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
    """Menu to equip artifacts into the ship's ability slots."""

    def __init__(self, ship, ability_bar) -> None:
        self.ship = ship
        self.ability_bar = ability_bar
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.artifact_rects: list[tuple[type[Artifact], pygame.Rect]] = []
        self.pending_artifact: type[Artifact] | None = None

    def handle_event(self, event) -> bool:
        if self.pending_artifact:
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
            ):
                idx = event.key - pygame.K_1
                art = self.pending_artifact()
                if idx < len(self.ship.artifacts):
                    self.ship.artifacts[idx] = art
                else:
                    while len(self.ship.artifacts) < idx:
                        self.ship.artifacts.append(art)
                    if len(self.ship.artifacts) == idx:
                        self.ship.artifacts.append(art)
                self.ability_bar.set_ship(self.ship)
                self.pending_artifact = None
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.pending_artifact = None
                return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for cls, rect in self.artifact_rects:
                if rect.collidepoint(event.pos):
                    self.pending_artifact = cls
                    return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True

        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        from artifact import AVAILABLE_ARTIFACTS

        screen.fill((20, 20, 40))
        title = font.render("Artifacts", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        self.artifact_rects.clear()
        x0, y0 = 20, 60
        w, h = 200, 30
        for i, cls in enumerate(AVAILABLE_ARTIFACTS):
            rect = pygame.Rect(x0, y0 + i * (h + 5), w, h)
            self.artifact_rects.append((cls, rect))
            color = (60, 60, 90)
            if self.pending_artifact is cls:
                color = (80, 80, 120)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            name = cls().name
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=rect.center))

        if self.pending_artifact:
            prompt = font.render(
                "Press 1-3 to assign slot", True, (255, 255, 255)
            )
            screen.blit(prompt, (240, 60))

        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("Close", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))

        # Draw current ability bar so the player knows which slot to replace
        self.ability_bar.draw(screen, font)


class SettingsWindow:
    """View and edit control bindings."""

    def __init__(self) -> None:
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.actions = list(controls.DEFAULT_BINDINGS.keys())
        self.editing: str | None = None
        self.row_rects: list[pygame.Rect] = []
        self.zoom_rect = pygame.Rect(0, 0, 0, 0)
        self.click_rect = pygame.Rect(0, 0, 0, 0)

    def handle_event(self, event) -> bool:
        if self.editing:
            if event.type == pygame.KEYDOWN:
                controls.set_key(self.editing, event.key)
                controls.save_bindings()
                self.editing = None
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for action, rect in zip(self.actions, self.row_rects):
                if rect.collidepoint(event.pos):
                    self.editing = action
                    break
            if self.zoom_rect.collidepoint(event.pos):
                current = settings.get_setting("zoom_with_wheel")
                settings.set_setting("zoom_with_wheel", not current)
                settings.save_settings()
                return False
            if self.click_rect.collidepoint(event.pos):
                current = settings.get_setting("click_to_move")
                settings.set_setting("click_to_move", not current)
                settings.save_settings()
                return False
        if event.type == pygame.KEYDOWN and event.key == controls.get_key("cancel"):
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill((20, 20, 40))
        title = font.render("Ajustes", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        x0, y0 = 20, 60
        row_h = 20
        col_x = 320
        self.row_rects = []
        for i, action in enumerate(self.actions):
            rect = pygame.Rect(x0, y0 + i * row_h, col_x - x0 - 10, row_h)
            self.row_rects.append(rect)
            color = (80, 80, 120) if action == self.editing else (20, 20, 40)
            pygame.draw.rect(screen, color, rect)
            action_label = action
            keyname = pygame.key.name(controls.get_key(action))
            action_txt = font.render(action_label, True, (255, 255, 255))
            key_txt = font.render(keyname, True, (255, 255, 255))
            screen.blit(action_txt, (x0 + 5, y0 + i * row_h))
            screen.blit(key_txt, (col_x, y0 + i * row_h))

        zoom_y = y0 + len(self.actions) * row_h + 10
        self.zoom_rect = pygame.Rect(x0, zoom_y, col_x - x0 - 10, row_h)
        pygame.draw.rect(screen, (60, 60, 90), self.zoom_rect)
        mode = "Rueda" if settings.get_setting("zoom_with_wheel") else "Q/E"
        zoom_txt = font.render(f"Zoom: {mode}", True, (255, 255, 255))
        screen.blit(zoom_txt, (x0 + 5, zoom_y))

        click_y = zoom_y + row_h + 5
        self.click_rect = pygame.Rect(x0, click_y, col_x - x0 - 10, row_h)
        pygame.draw.rect(screen, (60, 60, 90), self.click_rect)
        enabled = settings.get_setting("click_to_move")
        click_label = "Sí" if enabled else "No"
        click_txt = font.render(f"Mover con clics: {click_label}", True, (255, 255, 255))
        screen.blit(click_txt, (x0 + 5, click_y))

        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("Close", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))


class AbilityBar:
    """Display up to five ability slots at the bottom of the screen."""

    SLOT_COUNT = 4
    SLOT_W = 80
    SLOT_H = 40
    MARGIN = 5
    HYPER_W = 60

    def __init__(self) -> None:
        self.slots: list[tuple[str, str]] = [
            ("Boost", "LShift"),
            ("", "1"),
            ("", "2"),
            ("", "3"),
        ]
        self.ship = None
        self.rects: list[pygame.Rect] = []
        total_w = (
            self.SLOT_COUNT * (self.SLOT_W + self.MARGIN)
            - self.MARGIN
            + self.MARGIN
            + self.HYPER_W
        )
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        y = config.WINDOW_HEIGHT - self.SLOT_H - 80
        for i in range(self.SLOT_COUNT):
            rect = pygame.Rect(
                start_x + i * (self.SLOT_W + self.MARGIN), y, self.SLOT_W, self.SLOT_H
            )
            self.rects.append(rect)
        self.hyper_rect = pygame.Rect(
            start_x + self.SLOT_COUNT * (self.SLOT_W + self.MARGIN),
            y,
            self.HYPER_W,
            self.SLOT_H,
        )

    def set_ship(self, ship) -> None:
        self.ship = ship
        self._update_artifact_names()

    def _update_artifact_names(self) -> None:
        for i in range(3):
            name = ""
            if self.ship and i < len(self.ship.artifacts):
                name = self.ship.artifacts[i].name
            self.slots[1 + i] = (name, str(i + 1))

    def handle_event(self, event, ship) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hyper_rect.collidepoint(event.pos):
                return True
            for idx, rect in enumerate(self.rects):
                if rect.collidepoint(event.pos):
                    if idx == 0:
                        if ship.boost_charge >= 1.0:
                            ship.boost_time = config.BOOST_DURATION
                            ship.boost_charge = 0.0
                    elif idx >= 1:
                        ship.use_artifact(idx - 1, [])
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                idx = event.key - pygame.K_1
                ship.use_artifact(idx, [])
        return False

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
        pygame.draw.ellipse(screen, (60, 60, 90), self.hyper_rect)
        pygame.draw.ellipse(screen, (200, 200, 200), self.hyper_rect, 1)
        hyper_txt = font.render("Hyper", True, (255, 255, 255))
        hyper_rect = hyper_txt.get_rect(center=self.hyper_rect.center)
        screen.blit(hyper_txt, hyper_rect)


class HyperJumpMap:
    """Interactive map for selecting hyperjump destinations."""

    def __init__(
        self,
        ship,
        sectors,
        world_w: int,
        world_h: int,
        objects: list | None = None,
    ) -> None:
        self.ship = ship
        self.sectors = sectors
        self.world_w = world_w
        self.world_h = world_h
        self.objects = objects or []
        self.zoom = 0.2
        self.camera_x = ship.x
        self.camera_y = ship.y
        self.dragging = False
        self.destination: tuple[float, float] | None = None
        self.last_mouse = (0, 0)
        self.confirm_rect = pygame.Rect(
            config.WINDOW_WIDTH - 110, config.WINDOW_HEIGHT - 40, 100, 30
        )
        self.cancel_rect = pygame.Rect(10, config.WINDOW_HEIGHT - 40, 100, 30)

    def handle_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.confirm_rect.collidepoint(event.pos) and self.destination:
                    self.ship.start_hyperjump(*self.destination)
                    return True
                if self.cancel_rect.collidepoint(event.pos):
                    return True
                off_x = self.camera_x - config.WINDOW_WIDTH / (2 * self.zoom)
                off_y = self.camera_y - config.WINDOW_HEIGHT / (2 * self.zoom)
                wx = event.pos[0] / self.zoom + off_x
                wy = event.pos[1] / self.zoom + off_y
                self.destination = (wx, wy)
                self.last_mouse = event.pos
            elif event.button == 3:
                self.dragging = True
                self.last_mouse = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging or event.buttons[0]:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]
                self.camera_x -= dx / self.zoom
                self.camera_y -= dy / self.zoom
                self.last_mouse = event.pos
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill(config.BACKGROUND_COLOR)
        off_x = self.camera_x - config.WINDOW_WIDTH / (2 * self.zoom)
        off_y = self.camera_y - config.WINDOW_HEIGHT / (2 * self.zoom)
        for sector in self.sectors:
            sector.draw(screen, off_x, off_y, self.zoom)

        for obj in self.objects:
            if hasattr(obj, "draw_at"):
                obj.draw_at(screen, off_x, off_y, self.zoom)
            elif hasattr(obj, "ship") and hasattr(obj.ship, "draw_at"):
                obj.ship.draw_at(screen, off_x, off_y, self.zoom)
            elif hasattr(obj, "draw"):
                try:
                    obj.draw(screen, off_x, off_y, self.zoom)
                except TypeError:
                    try:
                        obj.draw(screen, None, off_x, off_y, self.zoom)
                    except Exception:
                        pass

        ship_pos = (
            int((self.ship.x - off_x) * self.zoom),
            int((self.ship.y - off_y) * self.zoom),
        )
        pygame.draw.circle(screen, (0, 255, 0), ship_pos, 4)

        if self.destination:
            dest_pos = (
                int((self.destination[0] - off_x) * self.zoom),
                int((self.destination[1] - off_y) * self.zoom),
            )
            pygame.draw.circle(screen, (255, 0, 0), dest_pos, 6, 1)
            pygame.draw.rect(screen, (60, 60, 90), self.confirm_rect)
            pygame.draw.rect(screen, (200, 200, 200), self.confirm_rect, 1)
            txt = font.render("Confirm", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=self.confirm_rect.center))

        pygame.draw.rect(screen, (60, 60, 90), self.cancel_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.cancel_rect, 1)
        txt = font.render("Cancel", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.cancel_rect.center))


class CarrierMoveMap:
    """Interactive map for moving a carrier via autopilot."""

    def __init__(
        self,
        carrier,
        sectors,
        world_w: int,
        world_h: int,
        objects: list | None = None,
    ) -> None:
        self.carrier = carrier
        self.sectors = sectors
        self.world_w = world_w
        self.world_h = world_h
        self.objects = objects or []
        self.zoom = 0.2
        self.camera_x = carrier.x
        self.camera_y = carrier.y
        self.dragging = False
        self.destination: tuple[float, float] | None = None
        self.last_mouse = (0, 0)
        self.move_rect = pygame.Rect(
            config.WINDOW_WIDTH - 110, config.WINDOW_HEIGHT - 40, 100, 30
        )
        self.cancel_rect = pygame.Rect(10, config.WINDOW_HEIGHT - 40, 100, 30)

    def handle_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.move_rect.collidepoint(event.pos) and self.destination:
                    dest = types.SimpleNamespace(x=self.destination[0], y=self.destination[1])
                    self.carrier.start_autopilot(dest)
                    return True
                if self.cancel_rect.collidepoint(event.pos):
                    return True
                off_x = self.camera_x - config.WINDOW_WIDTH / (2 * self.zoom)
                off_y = self.camera_y - config.WINDOW_HEIGHT / (2 * self.zoom)
                wx = event.pos[0] / self.zoom + off_x
                wy = event.pos[1] / self.zoom + off_y
                self.destination = (wx, wy)
                self.last_mouse = event.pos
            elif event.button == 3:
                self.dragging = True
                self.last_mouse = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging or event.buttons[0]:
                dx = event.pos[0] - self.last_mouse[0]
                dy = event.pos[1] - self.last_mouse[1]
                self.camera_x -= dx / self.zoom
                self.camera_y -= dy / self.zoom
                self.last_mouse = event.pos
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        screen.fill(config.BACKGROUND_COLOR)
        off_x = self.camera_x - config.WINDOW_WIDTH / (2 * self.zoom)
        off_y = self.camera_y - config.WINDOW_HEIGHT / (2 * self.zoom)
        for sector in self.sectors:
            sector.draw(screen, off_x, off_y, self.zoom)

        for obj in self.objects:
            if hasattr(obj, "draw_at"):
                obj.draw_at(screen, off_x, off_y, self.zoom)
            elif hasattr(obj, "ship") and hasattr(obj.ship, "draw_at"):
                obj.ship.draw_at(screen, off_x, off_y, self.zoom)
            elif hasattr(obj, "draw"):
                try:
                    obj.draw(screen, off_x, off_y, self.zoom)
                except TypeError:
                    try:
                        obj.draw(screen, None, off_x, off_y, self.zoom)
                    except Exception:
                        pass

        carrier_pos = (
            int((self.carrier.x - off_x) * self.zoom),
            int((self.carrier.y - off_y) * self.zoom),
        )
        pygame.draw.circle(screen, (0, 255, 0), carrier_pos, 4)

        if self.destination:
            dest_pos = (
                int((self.destination[0] - off_x) * self.zoom),
                int((self.destination[1] - off_y) * self.zoom),
            )
            pygame.draw.circle(screen, (255, 0, 0), dest_pos, 6, 1)
            pygame.draw.rect(screen, (60, 60, 90), self.move_rect)
            pygame.draw.rect(screen, (200, 200, 200), self.move_rect, 1)
            txt = font.render("Move", True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=self.move_rect.center))

        pygame.draw.rect(screen, (60, 60, 90), self.cancel_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.cancel_rect, 1)
        txt = font.render("Cancel", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.cancel_rect.center))


class CarrierWindow:
    """Display carrier status and hangar slots."""

    def __init__(self, carrier) -> None:
        self.carrier = carrier
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.move_rect = pygame.Rect(20, config.WINDOW_HEIGHT - 40, 100, 30)
        self.stop_rect = pygame.Rect(130, config.WINDOW_HEIGHT - 40, 100, 30)
        self.slot_rects: list[tuple[int, pygame.Rect]] = []
        self.deploy_rects: list[tuple[int, pygame.Rect]] = []
        self.deployed_ship = None
        self.request_move = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            if self.move_rect.collidepoint(event.pos):
                self.request_move = True
                return True
            if self.stop_rect.collidepoint(event.pos):
                self.carrier.cancel_autopilot()
                return False
            for idx, rect in self.deploy_rects:
                if rect.collidepoint(event.pos):
                    ship = self.carrier.deploy_ship(idx)
                    if ship:
                        self.deployed_ship = ship
                    return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        import math

        screen.fill((20, 20, 40))
        title = font.render("Carrier", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        hull_txt = font.render(f"Hull: {self.carrier.hull}", True, (255, 255, 255))
        screen.blit(hull_txt, (20, 50))
        speed = math.hypot(self.carrier.vx, self.carrier.vy)
        speed_txt = font.render(f"Speed: {speed:.1f}", True, (255, 255, 255))
        screen.blit(speed_txt, (20, 70))

        self.deploy_rects.clear()
        x0, y0 = 20, 110
        w, h = 200, 30
        for i, ship in enumerate(self.carrier.hangars):
            rect = pygame.Rect(x0, y0 + i * (h + 5), w, h)
            pygame.draw.rect(screen, (60, 60, 90), rect)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)
            if ship:
                name_txt = font.render(ship.name, True, (255, 255, 255))
                screen.blit(name_txt, name_txt.get_rect(midleft=(rect.x + 5, rect.centery)))
                d_rect = pygame.Rect(rect.right + 10, rect.y, 80, h)
                pygame.draw.rect(screen, (60, 60, 90), d_rect)
                pygame.draw.rect(screen, (200, 200, 200), d_rect, 1)
                d_txt = font.render("Deploy", True, (255, 255, 255))
                screen.blit(d_txt, d_txt.get_rect(center=d_rect.center))
                self.deploy_rects.append((i, d_rect))
            else:
                empty_txt = font.render("Empty", True, (255, 255, 255))
                screen.blit(empty_txt, empty_txt.get_rect(center=rect.center))

        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        close_txt = font.render("Close", True, (255, 255, 255))
        screen.blit(close_txt, close_txt.get_rect(center=self.close_rect.center))


def draw_charge_bar(
    screen: pygame.Surface,
    ratio: float,
    x: int,
    y: int,
    width: int = 100,
    height: int = 10,
) -> None:
    """Render a weapon charge bar."""
    pygame.draw.rect(screen, (60, 60, 90), (x, y, width, height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), 1)
    fill = int(width * max(0.0, min(1.0, ratio)))
    if fill > 0:
        pygame.draw.rect(screen, (200, 200, 50), (x, y, fill, height))


def draw_labeled_bar(
    screen: pygame.Surface,
    font: pygame.font.Font,
    label: str,
    ratio: float,
    x: int,
    y: int,
    width: int = 100,
    height: int = 10,
    color: tuple[int, int, int] = (200, 200, 50),
) -> None:
    """Draw a horizontal progress bar with ``label`` above it."""

    pygame.draw.rect(screen, (60, 60, 90), (x, y, width, height))
    pygame.draw.rect(screen, (200, 200, 200), (x, y, width, height), 1)
    fill = int(width * max(0.0, min(1.0, ratio)))
    if fill > 0:
        pygame.draw.rect(screen, color, (x, y, fill, height))
    if label:
        txt = font.render(label, True, (255, 255, 255))
        txt_rect = txt.get_rect(midbottom=(x + width // 2, y - 2))
        screen.blit(txt, txt_rect)


class CrewTransferWindow:
    """Simple interface to move crew between two ships."""

    def __init__(self, ship_a, ship_b) -> None:
        self.ship_a = ship_a
        self.ship_b = ship_b
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.left_rects: list[tuple[object, pygame.Rect]] = []
        self.right_rects: list[tuple[object, pygame.Rect]] = []

    def _crew_for_ship(self, ship) -> list:
        crew = []
        if getattr(ship, "pilot", None):
            crew.append(ship.pilot)
        crew.extend(list(getattr(ship, "passengers", [])))
        return crew

    def _remove_from_ship(self, ship, member) -> None:
        if getattr(ship, "pilot", None) is member:
            ship.remove_pilot()
        else:
            ship.remove_passenger(member)

    def _add_to_ship(self, ship, member) -> None:
        if getattr(ship, "pilot", None) is None:
            ship.assign_pilot(member)
        else:
            ship.add_passenger(member)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for member, rect in self.left_rects:
                if rect.collidepoint(event.pos):
                    self._remove_from_ship(self.ship_a, member)
                    self._add_to_ship(self.ship_b, member)
                    return False
            for member, rect in self.right_rects:
                if rect.collidepoint(event.pos):
                    self._remove_from_ship(self.ship_b, member)
                    self._add_to_ship(self.ship_a, member)
                    return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        width = 360
        height = 200
        rect = pygame.Rect((config.WINDOW_WIDTH - width) // 2, 100, width, height)
        pygame.draw.rect(screen, (30, 30, 60), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        title = font.render("Crew Transfer", True, (255, 255, 255))
        screen.blit(title, (rect.x + 5, rect.y + 5))

        left_title = font.render(getattr(self.ship_a, "name", "Ship A"), True, (255, 255, 255))
        right_title = font.render(getattr(self.ship_b, "name", "Ship B"), True, (255, 255, 255))
        screen.blit(left_title, (rect.x + 20, rect.y + 30))
        screen.blit(right_title, (rect.x + width // 2 + 20, rect.y + 30))

        self.left_rects.clear()
        self.right_rects.clear()
        y_start = rect.y + 55
        item_h = 25
        for i, member in enumerate(self._crew_for_ship(self.ship_a)):
            r = pygame.Rect(rect.x + 10, y_start + i * (item_h + 5), width // 2 - 20, item_h)
            pygame.draw.rect(screen, (60, 60, 90), r)
            pygame.draw.rect(screen, (200, 200, 200), r, 1)
            name = getattr(member, "name", member.__class__.__name__)
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=r.center))
            self.left_rects.append((member, r))
        for i, member in enumerate(self._crew_for_ship(self.ship_b)):
            r = pygame.Rect(rect.x + width // 2 + 10, y_start + i * (item_h + 5), width // 2 - 20, item_h)
            pygame.draw.rect(screen, (60, 60, 90), r)
            pygame.draw.rect(screen, (200, 200, 200), r, 1)
            name = getattr(member, "name", member.__class__.__name__)
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=r.center))
            self.right_rects.append((member, r))

        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        close_txt = font.render("Close", True, (255, 255, 255))
        screen.blit(close_txt, close_txt.get_rect(center=self.close_rect.center))


class ResearchWindow:
    """Display the technology tree and allow starting research."""

    def __init__(self, manager: ResearchManager) -> None:
        self.manager = manager
        self.levels = _compute_levels()
        self.rects = _layout_nodes(self.levels, config.WINDOW_WIDTH)
        self.selected: str | None = None
        self._start_rect: pygame.Rect | None = None
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 40, 10, 30, 30)

    def handle_event(self, event) -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            if self.selected and self._start_rect and self._start_rect.collidepoint(event.pos):
                self.manager.start(self.selected)
                return False
            self.selected = None
            for tid, rect in self.rects.items():
                if rect.collidepoint(event.pos):
                    self.selected = tid
                    break
        return False

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        draw_tree(screen, font, self.rects, self.manager)
        self._start_rect = draw_info(screen, font, self.selected, self.manager)
        pygame.draw.rect(screen, (60, 60, 90), self.close_rect)
        pygame.draw.rect(screen, (200, 200, 200), self.close_rect, 1)
        txt = font.render("X", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.close_rect.center))

