import math

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black

SHIP_COLOR = (255, 255, 255)
SHIP_SIZE = 20
# Ship acceleration is drastically increased for snappier movement
SHIP_ACCELERATION = 300  # pixels per second squared (5x default)
# Increased friction value so ships retain more of their velocity each frame,
# giving them a noticeably longer drift after moving.
SHIP_FRICTION = 0.96  # velocity retained each frame
# Bounce velocity multiplier when colliding with objects
BOUNCE_FACTOR = 1.0
# Maximum travel speed for manual control
SHIP_MAX_SPEED = 80  # reduced by 20% for slower travel
# Slightly slower autopilot speed to keep movement moderate
AUTOPILOT_SPEED = 64  # pixels per second when auto moving
PLANET_LANDING_SPEED = 64  # slower speed when approaching a planet

# --- Hull settings -----------------------------------------------------------
# Maximum hull value for the player's ship
PLAYER_MAX_HULL = 120

# --- Explorer/Boat movement -------------------------------------------------
# Reduced 25% from previous value to slow down on-foot movement
# Speeds reduced by 20% for a more relaxed pace
EXPLORER_SPEED = 76  # walking speed on a planet surface
# Boat movement slowed down by an additional 10%
BOAT_SPEED_LAND = 43  # slow boat speed when on land
BOAT_SPEED_WATER = 144  # slightly faster than walking when on water
STORM_SLOW_FACTOR = 0.5  # movement multiplier when inside a storm
STORM_COLOR = (180, 180, 220, 120)  # RGBA colour for storm overlays
STORM_WIND_STRENGTH = 30.0  # lateral push velocity inside storms (pixels/sec)
ICE_SLOW_FACTOR = 0.7  # movement multiplier when walking on ice
ICE_COLOR = (200, 230, 255, 100)  # RGBA colour for ice overlays
DESERT_FILTER_COLOR = (230, 220, 170, 140)  # RGBA filter used during sandstorms
DESERT_STORM_MIN_TIME = 8.0   # minimum duration for a desert storm
DESERT_STORM_MAX_TIME = 16.0  # maximum duration for a desert storm
DESERT_STORM_INTERVAL_MIN = 45.0  # minimum time between sandstorms
DESERT_STORM_INTERVAL_MAX = 90.0  # maximum time between sandstorms
SNOW_STORM_MIN_TIME = 8.0   # minimum duration for a snowstorm
SNOW_STORM_MAX_TIME = 16.0  # maximum duration for a snowstorm
SNOW_STORM_INTERVAL_MIN = 60.0  # minimum time between snowstorms
SNOW_STORM_INTERVAL_MAX = 120.0  # maximum time between snowstorms
SNOW_STORM_PROBABILITY = 0.6  # chance of a snowstorm when interval ends
SNOW_STORM_COLOR = (220, 230, 255, 150)  # RGBA filter used during snowstorms
ICE_CRACK_PROBABILITY = 0.05  # chance per second that ice breaks underfoot
ICE_HOLE_DURATION = 6.0  # seconds before a cracked hole freezes over
EXPLORER_MAX_HEALTH = 100  # maximum health for the on-foot explorer
LAVA_DAMAGE_RATE = 25      # damage per second when standing in lava
LAVA_GEYSER_INTERVAL_MIN = 4.0  # minimum seconds between geyser eruptions
LAVA_GEYSER_INTERVAL_MAX = 8.0  # maximum seconds between geyser eruptions
LAVA_GEYSER_DURATION = 1.5       # duration of an eruption in seconds
LAVA_GEYSER_DAMAGE = 40          # damage per second from erupting geysers
LAVA_RIVER_SPEED = 10.0          # pixels per second that lava rivers drift
ERUPTION_CRYSTAL_CHANCE = 0.1    # probability of crystals spawning after an eruption

TREMOR_INTERVAL_MIN = 12.0  # shortest delay between random tremors
TREMOR_INTERVAL_MAX = 25.0  # longest delay between random tremors
TREMOR_DURATION = 0.8       # how long a tremor lasts
TREMOR_SHAKE = 5            # camera shake intensity during a tremor
TOXIC_GAS_COLOR = (100, 150, 80, 150)  # RGBA colour for poisonous clouds
TOXIC_GAS_DAMAGE = 15            # damage per second inside toxic gas
RESIDUE_EXTRACTION_DAMAGE = 10   # health lost when harvesting toxic waste

ORBIT_SPEED_FACTOR = 0.005  # base factor used to calculate orbital speed
SHIP_ORBIT_SPEED = 1.5      # angular speed for attack orbits (radians per second)
ORBIT_COOLDOWN = 5.0        # delay before a new orbit can be triggered
ORBIT_PROJECTILE_SPEED_MULTIPLIER = 2.0  # bullet speed boost while orbiting
ORBIT_PROJECTILE_CURVATURE = 4.0        # radians per second of bullet curve
ORBIT_TRIGGER_RANGE = 350   # max distance to start an orbit
PROJECTILE_MAX_DISTANCE = 1200          # maximum distance a projectile can travel
HOMING_PROJECTILE_TURN_RATE = 6.0       # rad/s a guided projectile can turn
PIRATE_TURRET_RANGE = 500               # engagement range for Pirate capital turrets

SECTOR_WIDTH = 2000
SECTOR_HEIGHT = 2000
GRID_SIZE = 3

# Minimum distance allowed between star systems when generated
MIN_SYSTEM_DISTANCE = 400

# Ship boost settings
BOOST_MULTIPLIER = 2.5  # speed multiplier when boost is active
BOOST_DURATION = 4.0    # seconds of boost
BOOST_RECHARGE = 10.0   # seconds to fully recharge boost

# Particle effects for ship thrusters
SHIP_PARTICLE_MAX = 80         # maximum number of exhaust particles
SHIP_PARTICLE_DURATION = 0.6   # lifetime of each exhaust particle in seconds
# Exhaust particles fade from a neutral gray tone
SHIP_PARTICLE_COLOR = (180, 180, 180)

# Camera speed when planning a route
CAMERA_PAN_SPEED = 500  # pixels per second
CAMERA_RECENTER_SPEED = 3.0  # how quickly the camera returns to the player
CAMERA_RECENTER_DELAY = 0.5  # pause after panning before recentering

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

# Portal settings for the Free Explorers
PORTAL_RADIUS = 15
PORTAL_COLOR = (0, 220, 0)
PORTAL_NEAR_DISTANCE = 300
PORTAL_PAIR_MIN_DISTANCE = 800
PORTAL_COOLDOWN = 1.0
PORTAL_USE_COST = 10


# Speed multiplier applied to all computer controlled ships and drones
# Use the same speed factor for all ships so they travel evenly
NPC_SPEED_FACTOR = 1.0

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
# Appearance of the trail shown during a hyperjump
HYPERJUMP_TRAIL_WIDTH = 12
HYPERJUMP_TRAIL_COLOR = (80, 150, 255)
HYPERJUMP_TRAIL_INNER_COLOR = (255, 255, 255)
# Color of the brief shock effect when entering hyperspace
HYPERJUMP_SHOCK_COLOR = (255, 120, 50)
# --- Defensive drone settings -------------------------------------------------
# Standard orbit radius is based on the owner's size
DEF_DRONE_ORBIT_RADIUS_FACTOR = 3.0
# Drones orbit slowly when idle
DEF_DRONE_ORBIT_SPEED = 0.8
# Aggressive speed when intercepting threats
DEF_DRONE_INTERCEPT_SPEED = 180.0
# How far a drone may wander from its patrol route
DEF_DRONE_MAX_ROAM_FACTOR = 3.0  # multiplier of the orbit radius
# Fixed radius to wander around the owner when patrolling
DEF_DRONE_PATROL_RADIUS = 120
# Detection radius for nearby threats or projectiles
DEF_DRONE_DETECTION_RANGE = 250
# Learning parameters used by the intelligent drone variant
DEF_DRONE_ALPHA = 0.5
DEF_DRONE_GAMMA = 0.9
DEF_DRONE_EPSILON = 0.1

# --- Light channeler settings -----------------------------------------------
# Energy transferred each second from a channeler to its battery
CHANNELER_TRANSFER_RATE = 10.0
# Maximum energy capacity of a battery
BATTERY_MAX_ENERGY = 200.0
# Hit points for Light Channeler components
CHANNELER_HP = 30.0
BATTERY_HP = 40.0
STAR_TURRET_HP = 60.0
# Energy consumed per shot when the StarTurret is connected to the battery
STAR_TURRET_ENERGY_PER_SHOT = 1.0
# Hit points lost per second when the turret is disconnected
STAR_TURRET_DISCONNECTED_LOSS = 1.0
# Seconds between shots for a cadence of 100 rounds per minute
CADENCE_100_RPM = 60.0 / 400.0
# Seconds between shots for a cadence of 30 rounds per minute
CADENCE_30_RPM = 60.0 / 120.0

# Deployment timing for LightChannelerWeapon components
CHANNELER_BATTERY_DELAY = 2.0  # seconds before the battery becomes visible
CHANNELER_TURRET_DELAY = 5.0   # seconds before the turret activates

# Firing parameters for the star turret
STAR_TURRET_ARC = math.pi * 0.1
STAR_TURRET_PROJECTILE_SPEED = 380
STAR_TURRET_PROJECTILE_DAMAGE = 6
# Maximum distance for star turret projectiles (30% shorter than default)
STAR_TURRET_PROJECTILE_MAX_DISTANCE = PROJECTILE_MAX_DISTANCE * 0.5

# Space station economy settings
STATION_RESTOCK_TIME = 60.0
STATION_PRICE_FLUCT = 0.05
# Prices are updated roughly once per second
STATION_PRICE_UPDATE_PERIOD = 1.0
# Clamp how far prices may deviate from the base item value
STATION_MIN_PRICE_MULT = 0.5
STATION_MAX_PRICE_MULT = 1.5

