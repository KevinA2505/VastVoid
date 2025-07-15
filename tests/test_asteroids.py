import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from asteroid import Asteroid
from star_system import StarSystem


def test_asteroid_resistance_tracks_resources():
    ast = Asteroid(0, 0, 3, "rocky", resources=10)
    assert ast.resistance == 10
    ast.mine(4)
    assert ast.resources == 6
    assert ast.resistance == 6


def test_depleted_asteroid_removed_from_system():
    sys = StarSystem(0, 0)
    asteroid = Asteroid(0, 0, 2, "icy", resources=3)
    sys.asteroids = [asteroid]
    asteroid.mine(3)
    sys.update()
    assert asteroid not in sys.asteroids
