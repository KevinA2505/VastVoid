from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set
import json

from items import ITEMS_BY_NAME, ItemType


@dataclass
class Recipe:
    """Simple crafting recipe."""

    result: str
    ingredients: Dict[str, int]
    time: float = 0.0
    energy: float = 0.0
    quantity: int = 1
    research: str | None = None

    def validate(self) -> None:
        if self.result not in ITEMS_BY_NAME:
            raise ValueError(f"Unknown result item: {self.result}")

        result_type = ITEMS_BY_NAME[self.result].tipo

        for name in self.ingredients:
            if name not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown ingredient: {name}")
            if (
                result_type in (ItemType.ARMA, ItemType.ARTEFACTO)
                and ITEMS_BY_NAME[name].tipo is ItemType.MATERIA_PRIMA
            ):
                raise ValueError(
                    "Recipes for armas or artefactos cannot use materia prima"
                )


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "crafting_recipes.json"


def _load_recipes() -> List[Recipe]:
    with DATA_FILE.open(encoding="utf-8") as fh:
        data = json.load(fh)

    recipes: List[Recipe] = []
    for entry in data:
        recipe = Recipe(
            entry["result"],
            {k: int(v) for k, v in entry["ingredients"].items()},
            entry.get("time", 0.0),
            entry.get("energy", 0.0),
            entry.get("quantity", 1),
            entry.get("research"),
        )
        recipe.validate()
        recipes.append(recipe)
    return recipes


RECIPES: List[Recipe] = _load_recipes()


def can_craft(
    inventory: Dict[str, int], recipe: Recipe, features: Set[str] | None = None
) -> bool:
    """Return ``True`` if the requirements for ``recipe`` are met."""

    if recipe.research and (not features or recipe.research not in features):
        return False

    return all(inventory.get(name, 0) >= qty for name, qty in recipe.ingredients.items())
