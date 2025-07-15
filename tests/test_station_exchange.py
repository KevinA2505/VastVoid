import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from character import Human, Player
from fraction import FRACTIONS
from station import EXCHANGE_RATE, SpaceStation


def test_exchange_basic():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    player.add_item("hierro", 2)
    station = SpaceStation(0, 0)
    gained = station.exchange_for_credits(player, "hierro", 2)
    assert gained == int(5 * 2 * EXCHANGE_RATE)
    assert player.credits == gained
    assert player.inventory["hierro"] == 0


def test_exchange_cosmic_bonus():
    guild = next(f for f in FRACTIONS if f.name == "Cosmic Guild")
    player = Player("Test", 20, Human(), guild)
    player.add_item("hierro", 2)
    station = SpaceStation(0, 0)
    gained = station.exchange_for_credits(player, "hierro", 2)
    assert gained == int(5 * 2 * EXCHANGE_RATE * 1.1)
    assert player.credits == gained
    assert player.inventory["hierro"] == 0
