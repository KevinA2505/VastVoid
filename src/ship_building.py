from dataclasses import dataclass
from typing import Dict, List

from ship import Ship, ShipModel, SHIP_MODELS
from character import Player


@dataclass
class ShipBlueprint:
    """Define required parts to build a ship model."""

    model: ShipModel
    parts: Dict[str, int]


BLUEPRINTS: List[ShipBlueprint] = [
    ShipBlueprint(
        SHIP_MODELS[0],
        {"motor basico": 1, "casco ligero": 1, "cabina estandar": 1},
    ),
    ShipBlueprint(
        SHIP_MODELS[1],
        {"motor avanzado": 1, "casco reforzado": 1, "cabina de lujo": 1},
    ),
]


def assemble_ship(player: Player, blueprint: ShipBlueprint) -> Ship | None:
    """Create a :class:`Ship` if ``player`` has all required parts."""

    if not all(
        player.inventory.get(name, 0) >= qty
        for name, qty in blueprint.parts.items()
    ):
        return None
    for name, qty in blueprint.parts.items():
        player.remove_item(name, qty)
    ship = Ship(0, 0, model=blueprint.model)
    if not hasattr(player, "fleet"):
        player.fleet = []
    player.fleet.append(ship)
    return ship
