import json
import os
from typing import List

from character import Player, Human, Alien, Robot
from fraction import FRACTIONS
from items import ITEM_NAMES
from ship import SHIP_MODELS, ShipModel

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")


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
    inv = {item: 0 for item in ITEM_NAMES}
    inv.update(data.get("inventory", {}))
    player.inventory = inv
    return player


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
