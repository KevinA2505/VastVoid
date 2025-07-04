from dataclasses import dataclass

@dataclass
class Fraction:
    """Represents a faction players can belong to."""
    name: str
    description: str
    boost: str

# Predefined fractions with simple boosts
FRACTIONS = [
    Fraction(
        name="Solar Dominion",
        description="Militaristic regime focused on expanding its stellar influence.",
        boost="Increases ship speed slightly",
    ),
    Fraction(
        name="Cosmic Guild",
        description="Alliance of traders and engineers controlling most commerce routes.",
        boost="Better prices at stations",
    ),
    Fraction(
        name="Nebula Order",
        description="Scholars dedicated to studying anomalies and black holes.",
        boost="Sensors reveal planets from farther away",
    ),
    Fraction(
        name="Pirate Clans",
        description="Loose coalition of outlaws thriving on ambush and stealth.",
        boost="Autopilot evades hazards more efficiently",
    ),
    Fraction(
        name="Free Explorers",
        description="Independent pilots seeking new frontiers beyond charted space.",
        boost="Faster boost recharge",
    ),
]
