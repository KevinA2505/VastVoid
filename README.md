# VastVoid

`VastVoid` is a small Pygame project that displays a world of star systems.
You can control a ship and travel across a plane populated by stars with
orbiting planets.
The core game classes now live in separate modules within `src` and are
initialized from a single entry point (`main.py`).

You can select any planet and choose **Visit planet** to land on its surface
and explore a procedurally generated map. Press `Escape` or use the *Take Off*
button to return to space.

## Features

* Land on planets to explore procedurally generated surfaces.
* Travel instantly via wormholes linking distant sectors.
* Engage hyper-speed travel to jump across the map
  (one-second charge with an eight-second cooldown).
* The Nebula Order flagship now displays three concentric circles: a dark
  purple outer hull, a mid purple ring with black markers at the cardinal
  points, and a light purple core. A thick golden **Engagement Ring** encircles
  the ship to host diplomats and other non-scientists.
* The flagship also fields defensive drones that orbit the vessel and intercept
  nearby threats.
* Ships can deploy a **Chrono Tachionic Whip** that slows enemies within a small field.

### Defensive drones
The Nebula Order flagship deploys a trio of small drones that protect only this
capital ship. They move in a slow patrol around the hull but react quickly to
incoming threats. Each drone relies on a lightweight learning
system provided by `drone_learning` to refine its response timing. They never
venture far from the flagship and engage threats solely within its immediate
vicinity.

### Chrono Tachionic Whip
This dual-phase weapon deploys a slowing field when ready. The field lasts five
seconds and reduces the speed of enemy ships within its radius by 20%.
While the field recharges (a 10&nbsp;second cooldown), the whip fires regular
shots like the basic weapon but with a 5% slower projectile speed and a 10%
shorter cooldown.

## Character creation

When starting the game you can personalise the player by entering a name,
age, species and a **fraction** (faction). Five fictional fractions are
available, each with a short description and a small boost for its members.
After the character is created you can also choose a starting ship from a
small catalogue of models, each with its own brand and classification.

Saved profiles are presented in a simple table when the game launches.
Each row lists the player's name alongside **Load** and **Delete** buttons,
and a separate *New Profile* button lets you create a fresh character.
New profiles are saved automatically once created so they appear on the list
the next time you run the game.

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

### Black holes
The ominous singularities exert their pull from farther away. Normal black
holes now affect ships within a 25% larger radius and feature a swirling
purple halo to emphasize their danger. Dark purple particles now orbit
throughout the entire pull range, and the gravitational force is 20% stronger.


A round **Hyper** button sits to the right of the slots. Clicking it opens a
large map of the surrounding sectors. Left-click anywhere on the map to place a
destination marker, then press **Confirm** to initiate a jump. Right-click and
drag to pan the view, or hold the left button to drag while pressed. Hyperjumps occur after a brief one-second delay and you must wait eight seconds before jumping again.
During the jump the ship violently streaks toward the destination while a large vignette darkens the screen. The travel time scales with distance using

```
v(d) = v0 · (1 + k · log10(1 + d / d0))
t(d) = d / v(d)
```

where `v0` is 4.0 pc/s, `d0` is 0.5 pc and `k` is 3.

Travel time is clamped between 1 and 60 seconds so even nearby jumps last at
least a second while distant ones never exceed a minute. The vignette overlay is
darker to emphasize the effect.

Projectiles now vanish after travelling around 1200 pixels. Shots fired while
orbiting curve sharply towards the target so they rarely miss. Normal shots
travel in a straight line.

### Artifacts
Ships can equip artifacts that provide situational abilities. The EMP now only
disables shields and triggers a visible shockwave around the player.
Along with the Area Shield, the **Gravity Tractor** now launches a probe toward
the selected point. After five seconds the probe deploys a miniature black hole
that tugs nearby ships 25% harder, covers a 15% wider radius and lasts
30&nbsp;seconds. This ability has a 35&nbsp;second cooldown before it can be
deployed again.

Three additional artifacts expand your tactical options:

* **Repair Bots** – releases nanobots that restore hull and shields over five
  seconds. This ability has a 15&nbsp;second cooldown.
* **Solar Link** – connects the ship to the nearest star within 500 pixels,
  boosting shield recharge and weapon rates for six seconds. It cannot be used
  if no star is close. Cooldown: 20&nbsp;seconds.
* **Decoy** – projects a fragile copy of the ship that lasts a few seconds or
  until destroyed. Activating it cloaks your ship for three seconds. Cooldown:
  18&nbsp;seconds.

Press **G** to open the artifact menu. All available artifacts are listed and
clicking one lets you choose the ability slot by pressing **1**, **2** or **3**.
The first slot (Boost) cannot be replaced.

### Energy and the Dyson Sphere

Stars now carry a vast reserve of power through a new `energy` attribute.
Capital ships include matching `energy` and `max_energy` values which default
to 10&nbsp;000 units. Solar Dominion flagships start with their energy bar full
thanks to the channel arms that surround them. Each arm links to a nearby star
and transfers roughly 10 energy per second while the link is maintained,
reducing the star's own supply. This mechanism lays the groundwork for
constructing a Dyson Sphere that continuously harvests stellar energy for the
faction's fleet.

### Free Explorers flagship and portals

The Free Explorers capital ship now appears as a round gray disk with a black
edge and a neutral gray aura. Four missile turrets sit near the extreme north,
south, east and west edges of the hull so they are spaced farther apart. These
launch homing missiles that deal 20% extra damage but travel 20%
slower than standard versions. Each missile detonates after a short lifetime,
producing a very small blast radius.

Three pairs of green portals also accompany the flagship. Half of each pair
spawns nearby while the distant counterpart is placed farther away. Members of
the Free Explorers use them freely, but other factions must pay 10 credits per
teleport.

### Crew management and docking

Each ship has a single pilot seat and two passenger slots. Press **C** when two vessels are close to attempt docking via the Common Berthing Mechanism. If docking succeeds a crew transfer window appears so you can move members between ships. Your starting ship also carries a robot named PEPE as an initial passenger.
