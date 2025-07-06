"""Aggressive drone that patrols the Nebula Order flagship's ring."""

from combat import Drone


class AggressiveDefensiveDrone(Drone):
    """A more combative drone orbiting around its owner."""

    def __init__(
        self,
        owner,
        radius: float,
        hp: float = 40.0,
        fire_cooldown: float = 0.2,
        orbit_speed: float = 1.0,
    ) -> None:
        super().__init__(owner, hp=hp, orbit_speed=orbit_speed)
        self.radius = radius
        self.fire_cooldown = fire_cooldown

