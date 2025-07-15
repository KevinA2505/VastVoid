import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ship_building import BLUEPRINTS, assemble_ship
from character import Player, Human
from fraction import FRACTIONS


def test_assemble_ship_success():
    bp = BLUEPRINTS[0]
    player = Player("Test", 20, Human(), FRACTIONS[0])
    for name, qty in bp.parts.items():
        player.add_item(name, qty)
    ship = assemble_ship(player, bp)
    assert ship is not None
    assert ship in player.fleet
    for name in bp.parts:
        assert player.inventory[name] == 0


def test_assemble_ship_missing_parts():
    bp = BLUEPRINTS[0]
    player = Player("Test", 20, Human(), FRACTIONS[0])
    # only add a subset of parts
    item = next(iter(bp.parts))
    player.add_item(item, bp.parts[item])
    ship = assemble_ship(player, bp)
    assert ship is None
    assert len(player.fleet) == 0
