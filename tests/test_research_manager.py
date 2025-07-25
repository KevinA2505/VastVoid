import sys
from pathlib import Path

# Make src importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from tech_tree import ResearchManager, TECH_TREE
from character import Player, Human
from fraction import FRACTIONS
from refinery import RECIPES, refine_item


def test_can_start_respects_prerequisites():
    mgr = ResearchManager()

    # "advanced_energy" requires "mining" to be completed first
    assert not mgr.can_start("advanced_energy")

    mgr.start("mining")
    mgr.advance(TECH_TREE["mining"].cost)

    assert mgr.can_start("advanced_energy")


def test_advance_completes_technology():
    mgr = ResearchManager()
    mgr.start("mining")

    # Progress below the cost should not finish research
    mgr.advance(TECH_TREE["mining"].cost / 2)
    assert "mining" not in mgr.completed
    assert mgr.in_progress["mining"] == TECH_TREE["mining"].cost / 2

    # Completing the remaining progress should finish the tech
    finished = mgr.advance(TECH_TREE["mining"].cost / 2)
    assert "mining" in finished
    assert "mining" in mgr.completed
    assert "mining" not in mgr.in_progress


def test_player_features_unlock_on_completion():
    mgr = ResearchManager()
    player = Player("Test", 30, Human(), FRACTIONS[0], research=mgr)

    player.research.start("mining")
    player.progress_research(TECH_TREE["mining"].cost)

    player.research.start("advanced_energy")
    # Halfway done should not unlock features
    player.progress_research(TECH_TREE["advanced_energy"].cost / 2)
    assert "Energy Shields" not in player.features

    player.progress_research(TECH_TREE["advanced_energy"].cost / 2)
    assert "Energy Shields" in player.features


def test_bonus_speeds_up_research():
    mgr = ResearchManager()
    mgr.start("mining")

    # With a 2x bonus, half the cost should finish the tech
    finished = mgr.advance(TECH_TREE["mining"].cost / 2, bonus=2.0)
    assert "mining" in finished
    assert "mining" in mgr.completed


def test_refinery_locked_until_research_completed():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    recipe = RECIPES[0]

    for inp in recipe.mapping:
        player.add_item(inp, 1)

    # Refining should fail before unlocking Ore Processing
    assert not refine_item(player, recipe)

    player.research.start("mining")
    player.progress_research(TECH_TREE["mining"].cost)

    # After completing the research, the helper should work
    assert refine_item(player, recipe)
    for inp, out in recipe.mapping.items():
        assert player.inventory[inp] == 0
        assert player.inventory[out] == recipe.quantity
