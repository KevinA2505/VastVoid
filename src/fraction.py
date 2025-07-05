from dataclasses import dataclass

Color = tuple[int, int, int]

@dataclass
class Fraction:
    """Represents a faction players can belong to."""
    name: str
    description: str
    boost: str
    color: Color
    shape: str
    aura: str

# Predefined fractions with simple boosts
FRACTIONS = [
    Fraction(
        name="Solar Dominion",
        description="Militaristic regime focused on expanding its stellar influence.",
        boost="Increases ship speed slightly",
        color=(255, 190, 70),
        shape="angular",
        aura="radiant",
    ),
    Fraction(
        name="Cosmic Guild",
        description="Alliance of traders and engineers controlling most commerce routes.",
        boost="Better prices at stations",
        color=(50, 200, 255),
        shape="round",
        aura="trade",
    ),
    Fraction(
        name="Nebula Order",
        description="Scholars dedicated to studying anomalies and black holes.",
        boost="Sensors reveal planets from farther away",
        color=(180, 70, 255),
        shape="sleek",
        aura="mystic",
    ),
    Fraction(
        name="Pirate Clans",
        description="Loose coalition of outlaws thriving on ambush and stealth.",
        boost="Autopilot evades hazards more efficiently",
        color=(200, 50, 50),
        shape="spiky",
        aura="shadow",
    ),
    Fraction(
        name="Free Explorers",
        description="Independent pilots seeking new frontiers beyond charted space.",
        boost="Faster boost recharge",
        color=(80, 255, 80),
        shape="streamlined",
        aura="adventure",
    ),
]
