import json
import os
from typing import List

from character import Player, Human, Alien, Robot
from fraction import FRACTIONS
from items import ITEMS_BY_NAME
from inventory import Inventory
from ship import SHIP_MODELS, ShipModel, Ship
from station import SpaceStation
from tech_tree import ResearchManager, TECH_TREE

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")


def _model_to_dict(model: ShipModel | None):
    if not model:
        return None
    return {
        "name": model.name,
        "classification": model.classification,
        "brand": model.brand,
    }


def _dict_to_model(data: dict | None) -> ShipModel | None:
    if not data:
        return None
    classification = data.get("classification")
    brand = data.get("brand")
    name = data.get("name")
    for m in SHIP_MODELS:
        if name:
            if (
                m.name == name
                and m.classification == classification
                and m.brand == brand
            ):
                return m
        else:
            if m.classification == classification and m.brand == brand:
                return m
    return None


def _ship_to_dict(ship: Ship | None):
    if not ship:
        return None
    return {
        "model": _model_to_dict(ship.model),
        "name": ship.name,
        "hull": ship.hull,
        "fuel": getattr(ship, "fuel", 0),
    }


def _dict_to_ship(data: dict | None) -> Ship | None:
    if not data:
        return None
    model = _dict_to_model(data.get("model"))
    ship = Ship(0, 0, model=model, hull=int(data.get("hull", 100)), fuel=float(data.get("fuel", 100)))
    ship.name = data.get("name", ship.name)
    if hasattr(ship, "fuel"):
        ship.fuel = data.get("fuel", ship.fuel)
    return ship


def _research_to_dict(mgr: ResearchManager | None):
    """Serialize a :class:`ResearchManager` to a dictionary."""
    if not mgr:
        return {"completed": [], "in_progress": {}}
    return {
        "completed": sorted(list(mgr.completed)),
        "in_progress": mgr.in_progress,
    }


def _dict_to_research(data: dict | None) -> ResearchManager:
    """Reconstruct a :class:`ResearchManager` from ``data``."""
    mgr = ResearchManager()
    if not data:
        return mgr
    mgr.completed = set(data.get("completed", []))
    mgr.in_progress = {k: float(v) for k, v in data.get("in_progress", {}).items()}
    return mgr


def save_player(player: Player) -> None:
    """Serialize Player data to JSON inside the saves directory."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, f"{player.name}.json")
    data = {
        "name": player.name,
        "age": player.age,
        "species": player.species.species,
        "fraction": player.fraction.name,
        "inventory": player.inventory.to_dict(),
        "credits": player.credits,
        "ship_model": _model_to_dict(player.ship_model),
        "research": _research_to_dict(getattr(player, "research", None)),
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
        research=_dict_to_research(data.get("research")),
    )
    inv = {name: 0 for name in ITEMS_BY_NAME}
    inv.update(data.get("inventory", {}))
    player.inventory = Inventory(inv)

    # Rebuild feature flags from completed research
    for tech_id in player.research.completed:
        node = TECH_TREE.get(tech_id)
        if node:
            player.features.update(node.unlocked_features)

    return player


def list_players() -> List[str]:
    """Return the list of saved player profile names."""
    if not os.path.isdir(SAVE_DIR):
        return []
    names = []
    for fname in os.listdir(SAVE_DIR):
        if fname.endswith(".json") and fname not in {"controls.json", "settings.json"}:
            names.append(os.path.splitext(fname)[0])
    return sorted(names)


def delete_player(name: str) -> None:
    """Delete the save file for the given player name."""
    path = os.path.join(SAVE_DIR, f"{name}.json")
    if os.path.exists(path):
        os.remove(path)


def ensure_admin_profile() -> None:
    """Create a developer profile named ``admin`` with everything unlocked."""
    admin_path = os.path.join(SAVE_DIR, "admin.json")
    if os.path.exists(admin_path):
        return

    research = ResearchManager()
    for tid in TECH_TREE:
        research.completed.add(tid)

    player = Player(
        name="admin",
        age=30,
        species=Human(),
        fraction=FRACTIONS[0],
        credits=999999,
        research=research,
    )

    for item in ITEMS_BY_NAME:
        player.inventory.add(item, 1)

    for node in TECH_TREE.values():
        player.features.update(node.unlocked_features)

    save_player(player)


def save_station_hangars(stations: List[SpaceStation]) -> None:
    """Persist hangar contents for each station."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, "stations.json")
    data = {}
    for st in stations:
        slots = [_ship_to_dict(h.occupied_by) for h in st.hangars]
        data[st.name] = slots
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_station_hangars(stations: List[SpaceStation]) -> None:
    """Load hangar contents from disk into existing stations."""
    path = os.path.join(SAVE_DIR, "stations.json")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {st.name: st for st in stations}
    for name, slots in data.items():
        station = mapping.get(name)
        if not station:
            continue
        for hangar, saved in zip(station.hangars, slots):
            hangar.occupied_by = _dict_to_ship(saved)
