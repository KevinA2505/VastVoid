from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List
import json


class Rarity(Enum):
    """Possible rarities for items."""

    COMUN = "comun"
    POCO_COMUN = "poco_comun"
    RARO = "raro"
    EPICO = "epico"


class ItemType(Enum):
    """Categories for items."""

    MATERIA_PRIMA = "materia_prima"
    COMBUSTIBLE = "combustible"
    OBJETO_RARO = "objeto_raro"
    ARTEFACTO = "artefacto"
    ARMA = "arma"
    HERRAMIENTA = "herramienta"
    PIEZA_NAVE = "pieza_nave"
    VEHICULO = "vehiculo"


@dataclass
class Item:
    """Small container for item data."""

    nombre: str
    tipo: ItemType
    peso: float
    valor: int
    descripcion: str
    rareza: Rarity


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "items.json"


def _load_items() -> Dict[str, List[Item]]:
    with DATA_FILE.open(encoding="utf-8") as fh:
        raw = json.load(fh)

    groups: Dict[str, List[Item]] = {}
    for gname, items in raw.items():
        group: List[Item] = []
        for itm in items:
            group.append(
                Item(
                    itm["nombre"],
                    ItemType(itm["tipo"]),
                    itm["peso"],
                    itm["valor"],
                    itm["descripcion"],
                    Rarity(itm["rareza"]),
                )
            )
        groups[gname] = group
    return groups


_groups = _load_items()

MATERIA_PRIMA: List[Item] = _groups.get("materia_prima", [])
COMBUSTIBLES: List[Item] = _groups.get("combustibles", [])
OBJETOS_RAROS: List[Item] = _groups.get("objetos_raros", [])
ARTEFACTOS: List[Item] = _groups.get("artefactos", [])
ARMAS: List[Item] = _groups.get("armas", [])
HERRAMIENTAS: List[Item] = _groups.get("herramientas", [])
PIEZAS_NAVE: List[Item] = _groups.get("piezas_nave", [])
VEHICULOS: List[Item] = _groups.get("vehiculos", [])

# Organize items by type for easy lookup
ITEMS_BY_TYPE: Dict[str, List[Item]] = {
    "materia_prima": MATERIA_PRIMA,
    "combustible": COMBUSTIBLES,
    "objeto_raro": OBJETOS_RAROS,
    "artefacto": ARTEFACTOS,
    "arma": ARMAS,
    "herramienta": HERRAMIENTAS,
    "pieza_nave": PIEZAS_NAVE,
    "vehiculo": VEHICULOS,
}

# Flatten list with all items
ITEMS: List[Item] = [item for group in ITEMS_BY_TYPE.values() for item in group]

# Fast lookup table by item name
ITEMS_BY_NAME: Dict[str, Item] = {item.nombre: item for item in ITEMS}


def get_item(name: str) -> Item:
    """Return the :class:`Item` matching ``name``."""
    return ITEMS_BY_NAME[name]

# List of item names for backwards compatibility
ITEM_NAMES: List[str] = list(ITEMS_BY_NAME.keys())
