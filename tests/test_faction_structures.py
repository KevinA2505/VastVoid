import sys
from pathlib import Path

# Ensure src is on the Python path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from faction_structures import CapitalShip, verify_pirate_turret_positions
from fraction import FRACTIONS


def test_verify_pirate_turret_positions():
    pirate_fraction = next(f for f in FRACTIONS if f.name == "Pirate Clans")
    ship = CapitalShip(name="Pirate Flagship")
    ship.apply_fraction_traits(pirate_fraction)
    assert verify_pirate_turret_positions(ship) is True

