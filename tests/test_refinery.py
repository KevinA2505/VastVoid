import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from refinery import RECIPES
from character import Player, Human
from fraction import FRACTIONS
from tech_tree import TECH_TREE


def test_refine_success():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    # unlock Ore Processing feature
    player.research.start("mining")
    player.progress_research(TECH_TREE["mining"].cost)

    recipe = RECIPES[0]
    for inp in recipe.mapping:
        player.add_item(inp, 1)

    assert player.refine_item(recipe)
    for inp, out in recipe.mapping.items():
        assert player.inventory[inp] == 0
        assert player.inventory[out] == 1


def test_refine_missing():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    player.research.start("mining")
    player.progress_research(TECH_TREE["mining"].cost)
    recipe = RECIPES[0]
    # do not add required input
    assert not player.refine_item(recipe)
    for inp, out in recipe.mapping.items():
        assert player.inventory[inp] == 0
        assert player.inventory[out] == 0


def test_refine_requires_research():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    recipe = RECIPES[0]
    for inp in recipe.mapping:
        player.add_item(inp, 1)
    # feature not unlocked
    assert not player.refine_item(recipe)
    for inp, out in recipe.mapping.items():
        assert player.inventory[inp] == 1
        assert player.inventory[out] == 0

