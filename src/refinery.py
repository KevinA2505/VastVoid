from dataclasses import dataclass
from typing import Dict

from items import ITEMS_BY_NAME


@dataclass
class RefineryRecipe:
    """Recipe for refining raw materials into processed goods."""

    mapping: Dict[str, str]
    time: float = 0.0
    energy: float = 0.0

    def validate(self) -> None:
        for inp, out in self.mapping.items():
            if inp not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown input item: {inp}")
            if out not in ITEMS_BY_NAME:
                raise ValueError(f"Unknown output item: {out}")


RECIPES = [
    RefineryRecipe({"hierro": "lingote de hierro"}),
    RefineryRecipe({"titanio": "placa de titanio"}),
]

for r in RECIPES:
    r.validate()


def can_refine(inventory: Dict[str, int], recipe: RefineryRecipe) -> bool:
    """Return ``True`` if ``inventory`` has all required inputs for ``recipe``."""
    return all(inventory.get(inp, 0) >= 1 for inp in recipe.mapping)


def refine_item(player: "Player", recipe: RefineryRecipe) -> bool:
    """Refine items according to ``recipe`` using ``player`` inventory."""
    from character import Player  # local import to avoid circular dependency

    if not can_refine(player.inventory, recipe):
        return False
    for inp, out in recipe.mapping.items():
        player.remove_item(inp)
        player.add_item(out)
    return True
