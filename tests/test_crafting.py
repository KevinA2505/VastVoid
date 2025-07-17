import sys
from pathlib import Path

# Make src importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from crafting import RECIPES
from character import Player, Human
from fraction import FRACTIONS


def test_craft_item_success():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    recipe = RECIPES[0]
    if recipe.research:
        player.features.add(recipe.research)
    for name, qty in recipe.ingredients.items():
        player.add_item(name, qty)
    assert player.craft_item(recipe)
    assert player.inventory[recipe.result] == recipe.quantity
    for name in recipe.ingredients:
        assert player.inventory[name] == 0


def test_craft_item_missing():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    recipe = RECIPES[1]
    if recipe.research:
        player.features.add(recipe.research)
    # add only part of ingredients
    for name, qty in list(recipe.ingredients.items())[:-1]:
        player.add_item(name, qty)
    assert not player.craft_item(recipe)
    assert player.inventory[recipe.result] == 0


def test_craft_requires_research():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    recipe = RECIPES[0]
    for name, qty in recipe.ingredients.items():
        player.add_item(name, qty)
    # Feature not granted
    assert not player.craft_item(recipe)
    assert player.inventory[recipe.result] == 0
