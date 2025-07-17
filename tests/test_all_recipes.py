import sys
from pathlib import Path

# Ensure src modules are importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from items import ITEMS_BY_NAME, ItemType
from crafting import RECIPES


def test_all_weapons_and_artifacts_have_recipes():
    recipes_by_result = {}
    for recipe in RECIPES:
        recipes_by_result.setdefault(recipe.result, []).append(recipe)

    for item in ITEMS_BY_NAME.values():
        if item.tipo in (ItemType.ARMA, ItemType.ARTEFACTO):
            assert item.nombre in recipes_by_result, f"No recipe for {item.nombre}"
            for recipe in recipes_by_result[item.nombre]:
                for ing in recipe.ingredients:
                    assert (
                        ITEMS_BY_NAME[ing].tipo is not ItemType.MATERIA_PRIMA
                    ), f"Recipe for {item.nombre} uses materia prima"
