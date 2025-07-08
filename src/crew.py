from dataclasses import dataclass

@dataclass
class CrewMember:
    """Simple data container representing a crew member."""

    name: str
    role: str = "Passenger"

__all__ = ["CrewMember"]
