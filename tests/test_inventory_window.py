import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pygame
import types

from ui import InventoryWindow
from character import Player, Human
from fraction import FRACTIONS
import items

pygame.font.init()
FONT = pygame.font.Font(None, 24)
SCREEN = pygame.Surface((800, 600))

class Dummy:
    def __init__(self, damage=0, fuel=0):
        self.damage = damage
        self.fuel = fuel


def setup_player():
    player = Player("Test", 20, Human(), FRACTIONS[0])
    player.inventory.clear()
    player.inventory.update({"alpha": 1, "beta": 1, "delta": 1})
    return player


def _draw_names(inv):
    inv.draw(SCREEN, FONT)
    return [name for name, _ in inv.item_rects]


def test_sort_by_name(monkeypatch):
    monkeypatch.setattr(items, "ITEMS_BY_NAME", {
        "alpha": Dummy(3, 1),
        "beta": Dummy(1, 5),
        "delta": Dummy(10, 0),
    })
    inv = InventoryWindow(setup_player())
    assert inv.sort_key == "name"
    names = _draw_names(inv)
    assert names == ["alpha", "beta", "delta"]


def test_sort_by_damage(monkeypatch):
    monkeypatch.setattr(items, "ITEMS_BY_NAME", {
        "alpha": Dummy(3, 1),
        "beta": Dummy(1, 5),
        "delta": Dummy(10, 0),
    })
    inv = InventoryWindow(setup_player())
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)
    inv.handle_event(event)
    names = _draw_names(inv)
    assert names == ["delta", "alpha", "beta"]


def test_sort_by_fuel(monkeypatch):
    monkeypatch.setattr(items, "ITEMS_BY_NAME", {
        "alpha": Dummy(3, 1),
        "beta": Dummy(1, 5),
        "delta": Dummy(10, 0),
    })
    inv = InventoryWindow(setup_player())
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f)
    inv.handle_event(event)
    names = _draw_names(inv)
    assert names == ["beta", "alpha", "delta"]
