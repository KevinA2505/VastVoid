import sys
from pathlib import Path

# Ensure src is on the Python path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from faction_structures import CapitalShip, PlanetOutpost, verify_pirate_turret_positions
from fraction import FRACTIONS
from tech_tree import ResearchManager


def test_verify_pirate_turret_positions():
    pirate_fraction = next(f for f in FRACTIONS if f.name == "Pirate Clans")
    ship = CapitalShip(name="Pirate Flagship")
    ship.apply_fraction_traits(pirate_fraction)
    assert verify_pirate_turret_positions(ship) is True


def test_outpost_research_bonus():
    nebula_fraction = next(f for f in FRACTIONS if f.name == "Nebula Order")
    outpost = PlanetOutpost(name="Test Outpost")
    mgr = ResearchManager()

    # Bonus from facilities only
    outpost.apply_fraction_traits(nebula_fraction, research=mgr, facilities=["Research Labs"])
    assert outpost.research_bonus == 0.1

    # Bonus from completed technology
    mgr.completed.add("deep_space")
    outpost.apply_fraction_traits(nebula_fraction, research=mgr)
    assert outpost.research_bonus == 0.1

    # Combined bonuses
    outpost.apply_fraction_traits(nebula_fraction, research=mgr, facilities=["Research Labs"])
    assert outpost.research_bonus == 0.2

