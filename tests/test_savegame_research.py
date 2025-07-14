import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import savegame
from character import Player, Human
from fraction import FRACTIONS
from tech_tree import ResearchManager, TECH_TREE


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
