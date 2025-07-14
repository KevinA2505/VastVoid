import sys
from pathlib import Path

# Make src importable
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from tech_tree import ResearchManager, TECH_TREE


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
