import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pygame

from ui import MarketWindow
from station import SpaceStation, EXCHANGE_RATE
from character import Player, Human
from fraction import FRACTIONS

SCREEN = pygame.Surface((800, 600))


class DummyFont:
    def __init__(self):
        self.texts = []

    def render(self, text, aa, color):
        self.texts.append(text)
        return pygame.Surface((1, 1))


def test_market_text(monkeypatch):
    player = Player("Test", 20, Human(), FRACTIONS[0])
    player.inventory.clear()
    player.inventory.add("hierro", 2)
    station = SpaceStation(0, 0)
    station.market = {"hierro": {"stock": 3, "price": 6}}
    market = MarketWindow(station, player)

    font = DummyFont()
    market.draw(SCREEN, font)

    assert "Buy hierro (3) - 6" in font.texts
    assert "Sell hierro (2) +5" in font.texts
    expected = int(2 * 5 * EXCHANGE_RATE)
    assert f"Exchange hierro (2) +{expected}" in font.texts
