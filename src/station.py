import math
import random
from dataclasses import dataclass

import pygame

from items import ITEMS, ITEMS_BY_NAME
from names import get_station_name

# Exchange rate when converting items directly into credits
EXCHANGE_RATE = 0.75


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

    def __init__(
        self,
        x: float,
        y: float,
        radius: int = 20,
        num_hangars: int = 3,
        num_rooms: int = 2,
    ) -> None:
        self.name = get_station_name()
        self.x = x
        self.y = y
        self.radius = radius
        self.hangars = [Hangar() for _ in range(num_hangars)]
        self.rooms = [Room(f"Room {i+1}") for i in range(num_rooms)]
        # Randomly populate the market with items for trade
        # Each entry maps item name -> {"stock": int, "price": int}
        self.market: dict[str, dict[str, int]] = {}
        self._restock_timer = 0.0
        self._price_timer = 0.0
        self._populate_market()

    def _populate_market(self) -> None:
        """Fill the station market with a selection of random items.

        Each item receives an initial stock and a price that fluctuates
        around the base value.
        """

        sample = random.sample(ITEMS, k=min(10, len(ITEMS)))
        for item in sample:
            self.market[item.nombre] = {
                "stock": random.randint(1, 5),
                "price": int(item.valor * random.uniform(0.8, 1.2)),
            }

    @staticmethod
    def random_station(star, distance: float) -> "SpaceStation":
        angle = random.uniform(0, 2 * math.pi)
        x = star.x + distance * math.cos(angle)
        y = star.y + distance * math.sin(angle)
        return SpaceStation(x, y)

    # --- Trading ---------------------------------------------------------

    def buy_item(self, player, item_name: str, qty: int = 1) -> bool:
        """Allow ``player`` to buy ``qty`` of ``item_name`` if available."""
        if item_name not in self.market or self.market[item_name]["stock"] < qty:
            return False
        item = ITEMS_BY_NAME[item_name]
        price = self.market[item_name]["price"] * qty
        if getattr(player, "fraction", None) and player.fraction.name == "Cosmic Guild":
            price = int(price * 0.9)
        if player.credits < price:
            return False
        player.credits -= price
        player.add_item(item_name, qty)
        self.market[item_name]["stock"] -= qty
        if self.market[item_name]["stock"] <= 0:
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
        if item_name in self.market:
            self.market[item_name]["stock"] += qty
        else:
            self.market[item_name] = {
                "stock": qty,
                "price": int(item.valor * random.uniform(0.8, 1.2)),
            }
        return True

    def exchange_for_credits(self, player, item_name: str, qty: int = 1) -> int:
        """Convert ``qty`` of ``item_name`` into credits.

        The base exchange rate is ``EXCHANGE_RATE`` times the item's value.
        Members of the *Cosmic Guild* receive a 10% bonus on the result.

        Returns the amount of credits gained, or ``0`` if the player lacks
        sufficient items.
        """

        if player.inventory.get(item_name, 0) < qty:
            return 0
        item = ITEMS_BY_NAME[item_name]
        rate = EXCHANGE_RATE
        if getattr(player, "fraction", None) and player.fraction.name == "Cosmic Guild":
            rate *= 1.1
        value = int(item.valor * qty * rate)
        player.remove_item(item_name, qty)
        player.credits += value
        return value

    def update(self, dt: float) -> None:
        """Update market prices and restock items over time."""
        import config

        self._restock_timer += dt
        self._price_timer += dt
        if self._restock_timer >= config.STATION_RESTOCK_TIME:
            self._restock_timer = 0.0
            self._restock()

        if self._price_timer >= config.STATION_PRICE_UPDATE_PERIOD:
            self._price_timer = 0.0
            self._update_prices()

    def _restock(self) -> None:
        """Increase stock of existing items and occasionally add new ones."""

        for data in self.market.values():
            data["stock"] += random.randint(1, 3)

        if len(self.market) < 10:
            available = [it for it in ITEMS if it.nombre not in self.market]
            if available:
                item = random.choice(available)
                self.market[item.nombre] = {
                    "stock": random.randint(1, 5),
                    "price": int(item.valor * random.uniform(0.8, 1.2)),
                }

    def _update_prices(self) -> None:
        """Apply periodic price fluctuations with clamping."""
        import config

        for name, data in self.market.items():
            base = ITEMS_BY_NAME[name].valor
            fluct = random.uniform(
                1 - config.STATION_PRICE_FLUCT,
                1 + config.STATION_PRICE_FLUCT,
            )
            new_price = data["price"] * fluct
            min_price = base * config.STATION_MIN_PRICE_MULT
            max_price = base * config.STATION_MAX_PRICE_MULT
            new_price = max(min_price, min(max_price, new_price))
            data["price"] = max(1, int(new_price))

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

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
        zoom: float = 1.0,
    ) -> None:
        scaled_radius = max(1, int(self.radius * zoom))
        pygame.draw.circle(
            screen,
            (180, 180, 200),
            (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom)),
            scaled_radius,
        )

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        """Return ``True`` if ``(x, y)`` is inside the station plus ``radius``."""
        return math.hypot(self.x - x, self.y - y) < self.radius + radius
