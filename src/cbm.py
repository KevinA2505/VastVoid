from __future__ import annotations

import math
from typing import TYPE_CHECKING
from crew import CrewMember

if TYPE_CHECKING:
    from ship import Ship


class CommonBerthingMechanism:
    """Simple docking mechanism allowing two ships to connect."""

    def __init__(self, host: Ship, range: float = 40.0) -> None:
        self.host = host
        self.range = range
        self.docked_to: Ship | None = None

    def can_dock(self, other_ship: Ship) -> bool:
        """Return ``True`` if ``other_ship`` is within docking range."""
        if self.docked_to is not None:
            return False
        distance = math.hypot(self.host.x - other_ship.x, self.host.y - other_ship.y)
        limit = self.range + self.host.collision_radius + other_ship.collision_radius
        return distance <= limit

    def dock(self, other_ship: Ship) -> bool:
        """Dock ``other_ship`` if within range."""
        if not self.can_dock(other_ship):
            return False
        self.docked_to = other_ship
        if getattr(other_ship, "cbm", None):
            other_ship.cbm.docked_to = self.host
        self.host.vx = self.host.vy = 0.0
        return True

    def undock(self) -> None:
        """Separate from any currently docked ship."""
        if self.docked_to and getattr(self.docked_to, "cbm", None):
            self.docked_to.cbm.docked_to = None
        self.docked_to = None

    def transfer_to_docked(self, member: CrewMember) -> bool:
        """Move ``member`` from the host ship to the docked ship."""
        if not self.docked_to:
            return False
        if member not in self.host.passengers:
            return False
        self.host.passengers.remove(member)
        self.docked_to.passengers.append(member)
        return True

    def transfer_from_docked(self, member: CrewMember) -> bool:
        """Move ``member`` from the docked ship back to the host."""
        if not self.docked_to:
            return False
        if member not in self.docked_to.passengers:
            return False
        self.docked_to.passengers.remove(member)
        self.host.passengers.append(member)
        return True

__all__ = ["CommonBerthingMechanism"]
