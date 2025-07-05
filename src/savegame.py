import json
import os
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from sector import Sector
    from station import SpaceStation

from character import Player, Human, Alien, Robot
from fraction import FRACTIONS
from items import ITEMS_BY_NAME
from ship import SHIP_MODELS, ShipModel

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
MARKET_FILE = os.path.join(SAVE_DIR, "station_markets.json")


def _model_to_dict(model: ShipModel | None):
    if not model:
        return None
    return {
        "classification": model.classification,
        "brand": model.brand,
    }


def _dict_to_model(data: dict | None) -> ShipModel | None:
    if not data:
        return None
    classification = data.get("classification")
    brand = data.get("brand")
    for m in SHIP_MODELS:
        if m.classification == classification and m.brand == brand:
            return m
    return None


def save_player(player: Player) -> None:
    """Serialize Player data to JSON inside the saves directory."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, f"{player.name}.json")
    data = {
        "name": player.name,
        "age": player.age,
        "species": player.species.species,
        "fraction": player.fraction.name,
        "inventory": player.inventory,
        "credits": player.credits,
        "ship_model": _model_to_dict(player.ship_model),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_station_markets(sectors: List["Sector"]):
    """Serialize market data for all stations in the world."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    markets: dict[str, dict[str, int]] = {}
    for sector in sectors:
        for system in sector.systems:
            for station in system.stations:
                markets[station.id] = station.market
    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump(markets, f, indent=2)


def load_player(name: str) -> Player:
    """Read JSON data and reconstruct a Player instance."""
    path = os.path.join(SAVE_DIR, f"{name}.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    species_map = {"Human": Human, "Alien": Alien, "Robot": Robot}
    species_cls = species_map.get(data.get("species"), Human)
    species = species_cls()
    fraction = next((f for f in FRACTIONS if f.name == data.get("fraction")), FRACTIONS[0])
    player = Player(
        data.get("name", name),
        int(data.get("age", 0)),
        species,
        fraction,
        ship_model=_dict_to_model(data.get("ship_model")),
        credits=int(data.get("credits", 0)),
    )
    inv = {name: 0 for name in ITEMS_BY_NAME}
    inv.update(data.get("inventory", {}))
    player.inventory = inv
    return player


def load_station_markets(sectors: List["Sector"]):
    """Restore saved station market data if present."""
    if not os.path.exists(MARKET_FILE):
        return
    with open(MARKET_FILE, "r", encoding="utf-8") as f:
        markets = json.load(f)
    for sector in sectors:
        for system in sector.systems:
            for station in system.stations:
                market = markets.get(station.id)
                if market is not None:
                    station.market = {k: int(v) for k, v in market.items()}


def list_players() -> List[str]:
    """Return the list of saved player profile names."""
    if not os.path.isdir(SAVE_DIR):
        return []
    names = []
    for fname in os.listdir(SAVE_DIR):
        if fname.endswith(".json"):
            names.append(os.path.splitext(fname)[0])
    return sorted(names)


def delete_player(name: str) -> None:
    """Delete the save file for the given player name."""
    path = os.path.join(SAVE_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
