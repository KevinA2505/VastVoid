import random

# Predefined lists of unique names for different objects
_STAR_NAMES = [
    "Arcturus",
    "Sirius",
    "Vega",
    "Betelgeuse",
    "Rigel",
    "Capella",
    "Aldebaran",
    "Procyon",
    "Spica",
    "Antares",
    "Altair",
    "Fomalhaut",
    "Deneb",
    "Pollux",
    "Regulus",
]

_PLANET_NAMES = [
    "Astra",
    "Borealis",
    "Cerulea",
    "Draconis",
    "Eldora",
    "Faunus",
    "Gaia",
    "Helios",
    "Icarus",
    "Juno",
    "Kaida",
    "Luminis",
    "Mystara",
    "Nereid",
    "Orion",
]

_SYSTEM_NAMES = [
    "Alpha Centauri",
    "Solaris",
    "Andromeda",
    "Nebulus",
    "Cygnus",
    "Orionis",
    "Lyra",
    "Pegasus",
    "Taurus",
    "Virgo",
    "Phoenix",
    "Aquila",
    "Perseus",
    "Draco",
    "Auriga",
]

_STATION_NAMES = [
    "Odyssey Station",
    "Zenith Hub",
    "Orion Dock",
    "Horizon Outpost",
    "Nova Base",
    "Eclipse Port",
    "Nebula Terminal",
    "Solstice Station",
    "Pioneer Post"
]

# Names for playable ships
_SHIP_NAMES = [
    "Valiant",
    "Nebula Runner",
    "Star Chaser",
    "Celestial Wind",
    "Lone Voyager",
    "Solar Flare",
    "Void Whisper",
    "Quantum Drift",
    "Cosmic Arrow",
    "Eclipse Rider",
]


def _get_name(pool: list) -> str:
    """Return and remove a random name from a pool."""
    if not pool:
        # Fallback if we run out of predefined names
        return f"Unknown{random.randint(1000, 9999)}"
    return pool.pop(random.randrange(len(pool)))


def get_star_name() -> str:
    return _get_name(_STAR_NAMES)


def get_planet_name() -> str:
    return _get_name(_PLANET_NAMES)


def get_system_name() -> str:
    return _get_name(_SYSTEM_NAMES)


def get_station_name() -> str:
    return _get_name(_STATION_NAMES)


def get_ship_name() -> str:
    return _get_name(_SHIP_NAMES)


PLANET_ENVIRONMENTS = [
    "rocky",
    "gas giant",
    "ocean world",
    "ice world",
    "desert",
    "lava",
    "forest",
    "toxic",
]
