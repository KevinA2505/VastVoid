import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

import pygame
import tech_tree
import tech_ui
from tech_tree import TechNode


def _build_tree():
    return {
        "a": TechNode("A", "", 0, [], []),
        "b": TechNode("B", "", 0, ["a"], []),
        "c": TechNode("C", "", 0, ["a"], []),
        "d": TechNode("D", "", 0, ["b", "c"], []),
    }



def test_compute_levels(monkeypatch):
    tree = _build_tree()
    monkeypatch.setattr(tech_tree, "TECH_TREE", tree)
    monkeypatch.setattr(tech_ui, "TECH_TREE", tree)

    levels = tech_ui._compute_levels()
    assert levels == {0: ["a"], 1: ["b", "c"], 2: ["d"]}


def test_layout_nodes(monkeypatch):
    tree = _build_tree()
    monkeypatch.setattr(tech_tree, "TECH_TREE", tree)
    monkeypatch.setattr(tech_ui, "TECH_TREE", tree)

    levels = tech_ui._compute_levels()
    rects = tech_ui._layout_nodes(levels, 500)

    assert rects["a"] == pygame.Rect(170, 60, 160, 40)
    assert rects["b"] == pygame.Rect(70, 180, 160, 40)
    assert rects["c"] == pygame.Rect(270, 180, 160, 40)
    assert rects["d"] == pygame.Rect(170, 300, 160, 40)
