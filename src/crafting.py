from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json

from items import ITEMS_BY_NAME


@dataclass
class Recipe:
    """Simple crafting recipe."""

    result: str
    ingredients: Dict[str, int]
    time: float = 0.0
    energy: float = 0.0

    def validate(self) -> None:
        if self.result not in ITEMS_BY_NAME:
            raise ValueError(f"Unknown result item: {self.result}")
        for name in self.ingredients:
            if name not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown ingredient: {name}")


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
        )
        recipe.validate()
        recipes.append(recipe)
    return recipes


RECIPES: List[Recipe] = _load_recipes()


def can_craft(inventory: Dict[str, int], recipe: Recipe) -> bool:
    """Return ``True`` if ``inventory`` has enough ingredients for ``recipe``."""
    return all(inventory.get(name, 0) >= qty for name, qty in recipe.ingredients.items())
