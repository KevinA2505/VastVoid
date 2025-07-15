from dataclasses import dataclass
from typing import Dict, List

from items import ITEMS_BY_NAME


@dataclass
class Recipe:
    """Simple crafting recipe."""

    result: str
    ingredients: Dict[str, int]

    def validate(self) -> None:
        if self.result not in ITEMS_BY_NAME:
            raise ValueError(f"Unknown result item: {self.result}")
        for name in self.ingredients:
            if name not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown ingredient: {name}")


RECIPES: List[Recipe] = [
    Recipe("rifle de plasma", {"pistola laser": 1, "combustible ionico": 2}),
    Recipe("lanzallamas", {"taladro": 1, "combustible de fusion": 1}),
    Recipe(
        "moto antigravitatoria",
        {"buggy lunar": 1, "bateria portatil": 2, "pico laser": 1},
    ),
    Recipe("generador de escudo", {"bateria portatil": 2, "cortador laser": 1}),
]

for r in RECIPES:
    r.validate()


def can_craft(inventory: Dict[str, int], recipe: Recipe) -> bool:
    """Return ``True`` if ``inventory`` has enough ingredients for ``recipe``."""
    return all(inventory.get(name, 0) >= qty for name, qty in recipe.ingredients.items())
