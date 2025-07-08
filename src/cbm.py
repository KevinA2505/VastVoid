import math
import pygame
import config

class CommonBerthingMechanism:
    """Simple representation of a CBM connecting two ships."""

    def __init__(self, ship_a, ship_b, range_px: float = 50.0) -> None:
        self.ship_a = ship_a
        self.ship_b = ship_b
        self.range_px = range_px
        self.docked = False

    def attempt_dock(self) -> bool:
        """Dock the two ships if they are within ``range_px`` distance."""
        dist = math.hypot(self.ship_a.x - self.ship_b.x, self.ship_a.y - self.ship_b.y)
        if dist <= self.range_px:
            self.docked = True
            return True
        return False

    def undock(self) -> None:
        """Release the connection between the ships."""
        self.docked = False

    def transfer_member(self, member, from_ship, to_ship) -> None:
        """Move ``member`` from ``from_ship`` to ``to_ship`` as a passenger."""
        if getattr(from_ship, "pilot", None) is member:
            from_ship.remove_pilot()
        else:
            from_ship.remove_passenger(member)
        to_ship.add_passenger(member)


class CrewTransferWindow:
    """Overlay to move crew between two docked ships."""

    def __init__(self, cbm: CommonBerthingMechanism) -> None:
        self.cbm = cbm
        self.close_rect = pygame.Rect(config.WINDOW_WIDTH - 110, 10, 100, 30)
        self.left_rects: list[tuple[object, pygame.Rect]] = []
        self.right_rects: list[tuple[object, pygame.Rect]] = []

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_rect.collidepoint(event.pos):
                return True
            for member, rect in self.left_rects:
                if rect.collidepoint(event.pos):
                    self.cbm.transfer_member(member, self.cbm.ship_a, self.cbm.ship_b)
                    return False
            for member, rect in self.right_rects:
                if rect.collidepoint(event.pos):
                    self.cbm.transfer_member(member, self.cbm.ship_b, self.cbm.ship_a)
                    return False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return True
        return False

    def _crew_for_ship(self, ship) -> list:
        crew = []
        if getattr(ship, "pilot", None):
            crew.append(ship.pilot)
        crew.extend(list(getattr(ship, "passengers", [])))
        return crew

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        width = 360
        height = 200
        rect = pygame.Rect((config.WINDOW_WIDTH - width) // 2, 100, width, height)
        pygame.draw.rect(screen, (30, 30, 60), rect)
        pygame.draw.rect(screen, (200, 200, 200), rect, 1)

        title = font.render("Crew Transfer", True, (255, 255, 255))
        screen.blit(title, (rect.x + 5, rect.y + 5))

        a_name = getattr(self.cbm.ship_a, "name", "Ship A")
        b_name = getattr(self.cbm.ship_b, "name", "Ship B")
        left_title = font.render(a_name, True, (255, 255, 255))
        right_title = font.render(b_name, True, (255, 255, 255))
        screen.blit(left_title, (rect.x + 20, rect.y + 30))
        screen.blit(right_title, (rect.x + width // 2 + 20, rect.y + 30))

        self.left_rects.clear()
        self.right_rects.clear()
        y_start = rect.y + 55
        item_h = 25
        # left ship crew
        for i, member in enumerate(self._crew_for_ship(self.cbm.ship_a)):
            r = pygame.Rect(rect.x + 10, y_start + i * (item_h + 5), width // 2 - 20, item_h)
            pygame.draw.rect(screen, (60, 60, 90), r)
            pygame.draw.rect(screen, (200, 200, 200), r, 1)
            name = getattr(member, "name", member.__class__.__name__)
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=r.center))
            self.left_rects.append((member, r))
        # right ship crew
        for i, member in enumerate(self._crew_for_ship(self.cbm.ship_b)):
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
