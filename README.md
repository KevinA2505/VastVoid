# VastVoid

`VastVoid` is a small Pygame project that displays a world of star systems.
You can control a ship and travel across a plane populated by stars with
orbiting planets.
The core game classes now live in separate modules within `src` and are
initialized from a single entry point (`main.py`).

You can select any planet and choose **Visit planet** to land on its surface
and explore a procedurally generated map. Press `Escape` or use the *Take Off*
button to return to space.

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

### Planet surfaces

Biomes now create irregular terrain patches instead of simple circles and
generate multiple item pickups. Approach an item to see its name displayed on
screen and know exactly what you are collecting.

The original example scripts (`black_plane.py`, `nave.py`, `space_objects.py`
and `colliding_star_systems.py`) remain in the `src` directory for reference.

Wormholes now appear at least once in every generated universe, allowing
instant travel between two distant points. The two ends of a pair are
placed far apart thanks to the `WORMHOLE_PAIR_MIN_DISTANCE` setting.

### Enemy AI

A new `Enemy` class lives in `src/enemy.py`. It creates autonomous pilots
with their own ships and simple state-based behaviour. Enemies can pursue
the player, fire at close range, or retreat when their hull integrity is
low. When a new game starts, a random number of enemies is generated and
scattered across space. The amount varies between `MIN_ENEMIES` and
`MAX_ENEMIES` defined in `config.py`.
Each enemy now spawns with a random weapon drawn from the same arsenal
available to the player, so encounters can vary widely.

#### Behavior trees

Enemy logic now runs on a small behavior tree built with `py_trees`. Each
enemy ticks its tree every frame to decide whether to idle, pursue, attack or
flee. Actions inside the tree call the same ship methods as before so combat
and navigation work exactly like the earlier state machine implementation.

### Learning enemies
Enemies now use the experimental `LearningEnemy` class from
`src/enemy_learning.py`. It replaces the behaviour tree with a simple
Q-learning algorithm so that each enemy chooses actions like pursue or attack
based on a learned Q-table updated every frame. Enemies are spawned through the
`create_learning_enemy()` helper by default and will adapt slightly to the
player's tactics.

The Q-table for these enemies is saved to `learning_enemy_q_table.pkl` in the
project root when the game exits. Spawning enemies load this file if present so
their behaviour persists between sessions.

### Ability bar and attack orbit
Five ability slots now appear at the bottom of the screen. The first slot shows
the **Boost** ability which is still activated with the left **Shift** key. The
second slot triggers the **Orbit** skill using the **R** key or by clicking the
slot. When used, your ship orbits the nearest enemy at a reduced speed for five
seconds and automatically fires once every second. After the orbit ends there
is a short cooldown before it can be triggered again.

Projectiles now vanish after travelling around 1200 pixels. Shots fired while
orbiting curve sharply towards the target so they rarely miss. Normal shots
travel in a straight line.

### Artifacts
Ships can equip artifacts that provide situational abilities. Along with the EMP
and Area Shield, a new **Gravity Tractor** generates a miniature black hole that
weakly pulls nearby ships for 15 seconds. It has a 30&nbsp;second cooldown before
it can be deployed again.
