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


class ResearchManager:
    """Track the research state of the player."""

    def __init__(self) -> None:
        # Technologies fully researched
        self.completed: set[str] = set()
        # Technologies currently in progress with accumulated points
        self.in_progress: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Research control helpers
    # ------------------------------------------------------------------
    def can_start(self, tech_id: str) -> bool:
        """Return ``True`` if ``tech_id`` can be researched.

        Raises
        ------
        KeyError
            If a prerequisite references a non-existent technology ID.
        ValueError
            If the prerequisites form a cycle.
        """

        def check_cycle(curr: str, stack: set[str]) -> None:
            if curr in stack:
                raise ValueError(f"Cyclic prerequisite detected at '{curr}'")
            stack.add(curr)
            node = TECH_TREE.get(curr)
            if node is None:
                raise KeyError(f"Unknown technology id '{curr}'")
            for pre in node.prerequisites:
                if pre not in TECH_TREE:
                    raise KeyError(f"Prerequisite '{pre}' for '{curr}' does not exist")
                check_cycle(pre, stack)
            stack.remove(curr)

        node = TECH_TREE.get(tech_id)
        if node is None:
            return False
        check_cycle(tech_id, set())
        if tech_id in self.completed or tech_id in self.in_progress:
            return False
        return all(req in self.completed for req in node.prerequisites)

    def start(self, tech_id: str) -> bool:
        """Begin researching ``tech_id`` if possible."""
        if self.can_start(tech_id):
            self.in_progress[tech_id] = 0.0
            return True
        return False

    def advance(self, dt: float, bonus: float = 1.0) -> list[str]:
        """Advance all ongoing research by ``dt`` points applying ``bonus``."""
        finished: list[str] = []
        for tech_id in list(self.in_progress):
            progress = self.in_progress[tech_id] + dt * bonus
            cost = TECH_TREE[tech_id].cost
            if progress >= cost:
                finished.append(tech_id)
                self.completed.add(tech_id)
                del self.in_progress[tech_id]
            else:
                self.in_progress[tech_id] = progress
        return finished
