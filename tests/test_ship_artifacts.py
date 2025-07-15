import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ship import Ship
from artifact import AreaShieldArtifact
from character import Player, Human
from fraction import FRACTIONS


def test_area_shield_requires_research():
    ship = Ship(0, 0)
    player = Player("Test", 30, Human(), FRACTIONS[0])
    ship.assign_pilot(player)
    art = AreaShieldArtifact()
    art._timer = art.cooldown
    ship.artifacts = [art]

    # Without Energy Shields feature
    ship.use_artifact(0, [])
    assert ship.area_shield is None

    # Grant feature and try again
    player.features.add("Energy Shields")
    art._timer = art.cooldown
    ship.use_artifact(0, [])
    assert ship.area_shield is not None
