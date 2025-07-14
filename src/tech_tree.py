from dataclasses import dataclass

@dataclass
class TechNode:
    """Single technology node in the research tree."""

    name: str
    description: str
    cost: int
    prerequisites: list[str]
    unlocked_features: list[str]


TECH_TREE: dict[str, TechNode] = {
    "mining": TechNode(
        name="Mining Technology",
        description="Allows extraction of basic minerals from asteroids.",
        cost=100,
        prerequisites=[],
        unlocked_features=["Basic Mining Stations", "Ore Processing"],
    ),
    "advanced_energy": TechNode(
        name="Advanced Energy",
        description="Unlocks improved engines and energy weapons.",
        cost=200,
        prerequisites=["mining"],
        unlocked_features=["Energy Shields", "Laser Cannons"],
    ),
    "deep_space": TechNode(
        name="Deep Space Exploration",
        description="Enables long-range travel and exploration vessels.",
        cost=300,
        prerequisites=["advanced_energy"],
        unlocked_features=["Long-Range Sensors", "Hyperdrive"],
    ),
}
