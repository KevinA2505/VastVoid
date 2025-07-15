import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import tech_tree
import tech_ui
from tech_tree import TechNode, ResearchManager
import pytest


def test_cycle_detection(monkeypatch):
    invalid = {
        "a": TechNode("A", "", 0, ["b"], []),
        "b": TechNode("B", "", 0, ["a"], []),
    }
    monkeypatch.setattr(tech_tree, "TECH_TREE", invalid)
    monkeypatch.setattr(tech_ui, "TECH_TREE", invalid)
    with pytest.raises(ValueError):
        tech_ui._compute_levels()
    mgr = ResearchManager()
    with pytest.raises(ValueError):
        mgr.can_start("a")
