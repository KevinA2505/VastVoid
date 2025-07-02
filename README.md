# VastVoid

`VastVoid` is a small Pygame project that displays a world of star systems.
You can control a ship and travel across a plane populated by stars with
orbiting planets.
The core game classes now live in separate modules within `src` and are
initialized from a single entry point (`main.py`).

## Character creation

When starting the game you can personalise the player by entering a name,
age, species and a **fraction** (faction). Five fictional fractions are
available, each with a short description and a small boost for its members.
After the character is created you can also choose a starting ship from a
small catalogue of models, each with its own brand and classification.

## Running the game

```bash
python src/main.py
```

The original example scripts (`black_plane.py`, `nave.py`, `space_objects.py`
and `colliding_star_systems.py`) remain in the `src` directory for reference.
