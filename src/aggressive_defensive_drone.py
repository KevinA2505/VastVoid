"""Aggressive drone that patrols the Nebula Order flagship's ring."""

from combat import Drone


class AggressiveDefensiveDrone(Drone):
    """A more combative drone orbiting around its owner."""

    def __init__(self, owner, radius: float, hp: float = 40.0, fire_cooldown: float = 0.2) -> None:
        super().__init__(owner, hp=hp)
        self.radius = radius
        self.fire_cooldown = fire_cooldown

