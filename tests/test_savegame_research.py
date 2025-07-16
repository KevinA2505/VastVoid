import sys
from pathlib import Path
import json

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import savegame
from character import Player, Human
from fraction import FRACTIONS
from tech_tree import ResearchManager, TECH_TREE
from items import ITEMS_BY_NAME


def test_save_and_load_research(tmp_path):
    savegame.SAVE_DIR = str(tmp_path)

    mgr = ResearchManager()
    mgr.start("mining")
    mgr.advance(TECH_TREE["mining"].cost)
    mgr.start("advanced_energy")
    mgr.advance(50)

    player = Player("Test", 25, Human(), FRACTIONS[0], research=mgr)
    savegame.save_player(player)

    loaded = savegame.load_player("Test")
    assert loaded.research.completed == mgr.completed
    assert loaded.research.in_progress == mgr.in_progress


def test_new_items_in_default_inventory():
    player = Player("User", 20, Human(), FRACTIONS[0])
    assert set(player.inventory) == set(ITEMS_BY_NAME)


def test_load_inventory_with_missing_items(tmp_path):
    """Profiles without newer item names should load with quantity zero."""
    savegame.SAVE_DIR = str(tmp_path)

    player = Player("Test", 30, Human(), FRACTIONS[0])
    savegame.save_player(player)

    path = Path(savegame.SAVE_DIR) / "Test.json"
    data = json.loads(path.read_text())

    missing = ["fusion gel", "nitrometano"]
    for name in missing:
        data["inventory"].pop(name, None)

    path.write_text(json.dumps(data))

    loaded = savegame.load_player("Test")
    for name in missing:
        assert name in loaded.inventory
        assert loaded.inventory[name] == 0

