import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import savegame
from tech_tree import TECH_TREE


def test_ensure_admin_profile(tmp_path):
    savegame.SAVE_DIR = str(tmp_path)
    savegame.ensure_admin_profile()

    assert "admin" in savegame.list_players()

    player = savegame.load_player("admin")
    assert set(player.research.completed) == set(TECH_TREE)
    assert all(qty == 1 for qty in player.inventory.values())

    unlocked = set()
    for node in TECH_TREE.values():
        unlocked.update(node.unlocked_features)
    assert unlocked.issubset(player.features)
