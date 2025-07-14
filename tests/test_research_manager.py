import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from tech_tree import ResearchManager, TECH_TREE


def test_research_flow():
    mgr = ResearchManager()

    # Start basic technology
    assert mgr.can_start("mining") is True
    assert mgr.start("mining") is True

    # Prerequisite not met yet
    assert mgr.can_start("advanced_energy") is False

    # Complete mining
    mgr.advance(TECH_TREE["mining"].cost)
    assert "mining" in mgr.completed
    assert "mining" not in mgr.in_progress

    # Now advanced_energy can begin
    assert mgr.can_start("advanced_energy") is True
    mgr.start("advanced_energy")
    mgr.advance(TECH_TREE["advanced_energy"].cost / 2)
    assert mgr.in_progress["advanced_energy"] == TECH_TREE["advanced_energy"].cost / 2
    mgr.advance(TECH_TREE["advanced_energy"].cost / 2)
    assert "advanced_energy" in mgr.completed
