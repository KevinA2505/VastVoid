from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import json

from items import ITEMS_BY_NAME


@dataclass
class RefineryRecipe:
    """Recipe for refining raw materials into processed goods."""

    mapping: Dict[str, str]
    time: float = 0.0
    energy: float = 0.0
    quantity: int = 1

    def validate(self) -> None:
        for inp, out in self.mapping.items():
            if inp not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown input item: {inp}")
            if out not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown output item: {out}")


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "refinery_recipes.json"


def _load_recipes() -> List[RefineryRecipe]:
    with DATA_FILE.open(encoding="utf-8") as fh:
        data = json.load(fh)

    recipes: List[RefineryRecipe] = []
    for entry in data:
        recipe = RefineryRecipe(
            {k: v for k, v in entry["mapping"].items()},
            entry.get("time", 0.0),
            entry.get("energy", 0.0),
            entry.get("quantity", 1),
        )
        recipe.validate()
        recipes.append(recipe)
    return recipes


RECIPES: List[RefineryRecipe] = _load_recipes()


def can_refine(inventory: Dict[str, int], recipe: RefineryRecipe) -> bool:
    """Return ``True`` if ``inventory`` has all required inputs for ``recipe``."""
    return all(inventory.get(inp, 0) >= 1 for inp in recipe.mapping)


def refine_item(player: "Player", recipe: RefineryRecipe) -> bool:
    """Refine items according to ``recipe`` using ``player`` inventory.

    The player must have completed the ``Ore Processing`` research before any
    refining can occur. This mirrors the behaviour of ``Player.refine_item``
    and allows tests to invoke this helper directly.
    """
    from character import Player  # local import to avoid circular dependency

    if "Ore Processing" not in player.features:
        return False
    if not can_refine(player.inventory, recipe):
        return False
    for inp, out in recipe.mapping.items():
        player.remove_item(inp)
        player.add_item(out, recipe.quantity)
    return True
