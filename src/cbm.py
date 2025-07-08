import math
import pygame
import config


class DockingAnimation:
    """Animate two ships moving into a docked position."""

    def __init__(self, ship_a, ship_b, distance: float = 30.0, duration: float = 3.0) -> None:
        self.ship_a = ship_a
        self.ship_b = ship_b
        self.distance = distance
        self.duration = duration
        self.elapsed = 0.0

        self.a_start = (ship_a.x, ship_a.y, ship_a.angle)
        self.b_start = (ship_b.x, ship_b.y, ship_b.angle)
        self.final_angle = (ship_a.angle + ship_b.angle) / 2
        mid_x = (ship_a.x + ship_b.x) / 2
        mid_y = (ship_a.y + ship_b.y) / 2
        self.a_end = (
            mid_x - math.cos(self.final_angle) * distance / 2,
            mid_y - math.sin(self.final_angle) * distance / 2,
        )
        self.b_end = (
            mid_x + math.cos(self.final_angle) * distance / 2,
            mid_y + math.sin(self.final_angle) * distance / 2,
        )
        self.done = False

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _lerp_angle(self, a: float, b: float, t: float) -> float:
        diff = math.atan2(math.sin(b - a), math.cos(b - a))
        return a + diff * t

    def update(self, dt: float) -> None:
        if self.done:
            return
        self.elapsed += dt
        t = min(1.0, self.elapsed / self.duration)
        ax = self._lerp(self.a_start[0], self.a_end[0], t)
        ay = self._lerp(self.a_start[1], self.a_end[1], t)
        bx = self._lerp(self.b_start[0], self.b_end[0], t)
        by = self._lerp(self.b_start[1], self.b_end[1], t)
        self.ship_a.x, self.ship_a.y = ax, ay
        self.ship_b.x, self.ship_b.y = bx, by
        self.ship_a.angle = self._lerp_angle(self.a_start[2], self.final_angle, t)
        self.ship_b.angle = self._lerp_angle(self.b_start[2], self.final_angle, t)
        if t >= 1.0:
            self.done = True

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float, zoom: float) -> None:
        if self.done:
            return
        t = min(1.0, self.elapsed / self.duration)
        start = ((self.a_end[0] - offset_x) * zoom, (self.a_end[1] - offset_y) * zoom)
        end = ((self.b_end[0] - offset_x) * zoom, (self.b_end[1] - offset_y) * zoom)
        mid = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
        dx = (end[0] - start[0]) / 2
        dy = (end[1] - start[1]) / 2
        draw_start = (mid[0] - dx * t, mid[1] - dy * t)
        draw_end = (mid[0] + dx * t, mid[1] + dy * t)
        pygame.draw.line(screen, (120, 120, 120), draw_start, draw_end, 4)

class CommonBerthingMechanism:
    """Simple representation of a CBM connecting two ships."""

    def __init__(self, ship_a, ship_b, range_px: float = 50.0) -> None:
        self.ship_a = ship_a
        self.ship_b = ship_b
        self.range_px = range_px
        self.docked = False
        self.animation: DockingAnimation | None = None

    def attempt_dock(self) -> bool:
        """Dock the two ships if they are within ``range_px`` distance."""
        dist = math.hypot(self.ship_a.x - self.ship_b.x, self.ship_a.y - self.ship_b.y)
        if dist <= self.range_px:
            self.docked = True
            return True
        return False

    def start_docking(self) -> None:
        """Begin a docking animation if ships are within range."""
        if self.docked or self.animation:
            return
        dist = math.hypot(self.ship_a.x - self.ship_b.x, self.ship_a.y - self.ship_b.y)
        if dist <= self.range_px:
            if hasattr(self.ship_a, "cancel_autopilot"):
                self.ship_a.cancel_autopilot()
            if hasattr(self.ship_b, "cancel_autopilot"):
                self.ship_b.cancel_autopilot()
            self.animation = DockingAnimation(self.ship_a, self.ship_b, self.range_px / 2)

    def undock(self) -> None:
        """Release the connection between the ships."""
        self.docked = False
        self.animation = None

    def transfer_member(self, member, from_ship, to_ship) -> None:
        """Move ``member`` from ``from_ship`` to ``to_ship`` as a passenger."""
        if getattr(from_ship, "pilot", None) is member:
            from_ship.remove_pilot()
        else:
            from_ship.remove_passenger(member)
        to_ship.add_passenger(member)


