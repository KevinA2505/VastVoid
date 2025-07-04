import pygame
import random
import math
from dataclasses import dataclass
from ..names import get_station_name
from ..mechanics.items import ITEMS, ITEMS_BY_NAME


@dataclass
class Hangar:
    occupied_by: object | None = None

    @property
    def occupied(self) -> bool:
        return self.occupied_by is not None


@dataclass
class Room:
    name: str


class SpaceStation:
    """Simple space station with hangars and recreational rooms."""

    def __init__(self, x: float, y: float, radius: int = 20,
                 num_hangars: int = 3, num_rooms: int = 2) -> None:
        self.name = get_station_name()
        self.x = x
        self.y = y
        self.radius = radius
        self.hangars = [Hangar() for _ in range(num_hangars)]
        self.rooms = [Room(f"Room {i+1}") for i in range(num_rooms)]
        # Randomly populate the market with items for trade
        self.market: dict[str, int] = {}
        self._populate_market()

    def _populate_market(self) -> None:
        """Fill the station market with a selection of random items."""
        sample = random.sample(ITEMS, k=min(10, len(ITEMS)))
        for item in sample:
            self.market[item.nombre] = random.randint(1, 5)

    @staticmethod
    def random_station(star, distance: float) -> "SpaceStation":
        angle = random.uniform(0, 2 * math.pi)
        x = star.x + distance * math.cos(angle)
        y = star.y + distance * math.sin(angle)
        return SpaceStation(x, y)

    # --- Trading ---------------------------------------------------------

    def buy_item(self, player, item_name: str, qty: int = 1) -> bool:
        """Allow ``player`` to buy ``qty`` of ``item_name`` if available."""
        if item_name not in self.market or self.market[item_name] < qty:
            return False
        item = ITEMS_BY_NAME[item_name]
        price = item.valor * qty
        if getattr(player, "fraction", None) and player.fraction.name == "Cosmic Guild":
            price = int(price * 0.9)
        if player.credits < price:
            return False
        player.credits -= price
        player.add_item(item_name, qty)
        self.market[item_name] -= qty
        if self.market[item_name] <= 0:
            del self.market[item_name]
        return True

    def sell_item(self, player, item_name: str, qty: int = 1) -> bool:
        """Buy items from the player."""
        if player.inventory.get(item_name, 0) < qty:
            return False
        item = ITEMS_BY_NAME[item_name]
        price = item.valor * qty
        if getattr(player, "fraction", None) and player.fraction.name == "Cosmic Guild":
            price = int(price * 1.1)
        player.credits += price
        player.remove_item(item_name, qty)
        self.market[item_name] = self.market.get(item_name, 0) + qty
        return True

    def has_free_hangar(self) -> bool:
        return any(not h.occupied for h in self.hangars)

    def dock_ship(self, ship) -> bool:
        for hangar in self.hangars:
            if not hangar.occupied:
                hangar.occupied_by = ship
                return True
        return False

    def undock_ship(self, ship) -> None:
        for hangar in self.hangars:
            if hangar.occupied_by is ship:
                hangar.occupied_by = None
                return

    def draw(self, screen: pygame.Surface, offset_x: float = 0,
             offset_y: float = 0, zoom: float = 1.0) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            (180, 180, 200),
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )
