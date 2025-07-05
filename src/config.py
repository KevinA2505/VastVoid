WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black

SHIP_COLOR = (255, 255, 255)
SHIP_SIZE = 20
# Ship acceleration is drastically increased for snappier movement
SHIP_ACCELERATION = 300  # pixels per second squared (5x default)
SHIP_FRICTION = 0.92  # velocity retained each frame
AUTOPILOT_SPEED = 120  # pixels per second when auto moving
PLANET_LANDING_SPEED = 100  # slower speed when approaching a planet

# --- Hull settings -----------------------------------------------------------
# Maximum hull values for player and enemy ships
PLAYER_MAX_HULL = 120
ENEMY_MAX_HULL = 80

# --- Explorer/Boat movement -------------------------------------------------
EXPLORER_SPEED = 150  # base walking speed on a planet surface
BOAT_SPEED_LAND = 60  # slow boat speed when on land
BOAT_SPEED_WATER = 200  # slightly faster than walking when on water

ORBIT_SPEED_FACTOR = 0.005  # base factor used to calculate orbital speed
SHIP_ORBIT_SPEED = 1.5      # angular speed for attack orbits (radians per second)
ORBIT_COOLDOWN = 5.0        # delay before a new orbit can be triggered
ORBIT_PROJECTILE_SPEED_MULTIPLIER = 2.0  # bullet speed boost while orbiting
ORBIT_PROJECTILE_CURVATURE = 4.0        # radians per second of bullet curve
ORBIT_TRIGGER_RANGE = 350   # max distance from an enemy to start an orbit
PROJECTILE_MAX_DISTANCE = 1200          # maximum distance a projectile can travel
HOMING_PROJECTILE_TURN_RATE = 6.0       # rad/s a guided projectile can turn

SECTOR_WIDTH = 2000
SECTOR_HEIGHT = 2000
GRID_SIZE = 3

# Minimum distance allowed between star systems when generated
MIN_SYSTEM_DISTANCE = 400

# Ship boost settings
BOOST_MULTIPLIER = 2.5  # speed multiplier when boost is active
BOOST_DURATION = 4.0    # seconds of boost
BOOST_RECHARGE = 10.0   # seconds to fully recharge boost

# Camera speed when planning a route
CAMERA_PAN_SPEED = 500  # pixels per second

# Black hole settings
BLACKHOLE_CHANCE = 0.15       # probability of a sector containing a black hole
BLACKHOLE_MIN_DISTANCE = 600  # minimum distance from any star system
# distance at which the ship feels the pull
BLACKHOLE_RANGE = 375         # increased by 25% for a stronger presence
BLACKHOLE_STRENGTH = 48000    # acceleration force applied when near (20% stronger)
BLACKHOLE_RADIUS = 25         # radius of the dangerous core
BLACKHOLE_FLASH_TIME = 1.0    # duration of whiteout when swallowed

# Worm hole settings
WORMHOLE_CHANCE = 0.05       # probability of a sector containing a wormhole pair
WORMHOLE_MIN_DISTANCE = 400  # minimum distance from star systems and black holes
# Minimum distance allowed between the two wormholes in a pair
WORMHOLE_PAIR_MIN_DISTANCE = 1200
WORMHOLE_RADIUS = 20         # visible size of a worm hole
WORMHOLE_COLOR = (150, 100, 200)
WORMHOLE_DELAY = 5.0         # seconds before teleport occurs
WORMHOLE_COOLDOWN = 3.0      # delay after teleport before re-entry allowed
WORMHOLE_FLASH_TIME = 0.75   # duration of post-teleport flash effect

# Enemy spawn settings
MIN_ENEMIES = 5
MAX_ENEMIES = 12

# Cooldown for enemy weapons in seconds. Default player weapons use
# 0.5, so enemies fire slightly faster but still allow the player to
# dodge incoming shots.
ENEMY_WEAPON_COOLDOWN = 0.3

# How often enemies attempt an orbit attack
ENEMY_ORBIT_INTERVAL = 12.0  # seconds between orbit attempts
ENEMY_ORBIT_PROBABILITY = 0.35  # chance of starting an orbit each interval

# --- Hyperjump settings ------------------------------------------------------
# Delay before a hyperjump completes and cooldown between jumps
HYPERJUMP_COOLDOWN = 8.0
HYPERJUMP_DELAY = 1.0
# Base hyperjump velocity in parsecs per second
# Further increased base hyperjump velocity (pc/s)
HYPERJUMP_BASE_SPEED = 6.0
# Shorter reference distance for noticeable scaling
HYPERJUMP_D0 = 0.5
# Stronger scaling so far targets only take a bit longer
HYPERJUMP_SPEED_SCALE = 3.0
# Conversion factor from world units to parsecs
HYPERJUMP_UNIT = 10.0
# Opacity of the vignette overlay during jumps
HYPERJUMP_VIGNETTE_ALPHA = 220

# Minimum and maximum duration of hyperjump animations in seconds
HYPERJUMP_MIN_TIME = 1.0
HYPERJUMP_MAX_TIME = 60.0

# --- Fuel settings -----------------------------------------------------------
# Conversion factor from item weight to fuel units
FUEL_PER_WEIGHT = 10
# Fuel consumed per second of normal thruster use
FUEL_BURN_RATE = 1.0
# Fuel cost to initiate a hyperjump
HYPERJUMP_FUEL_COST = 15
# Maximum fuel capacity used for UI gauge
FUEL_MAX = 100
