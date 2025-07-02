WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black

SHIP_COLOR = (255, 255, 255)
SHIP_SIZE = 20
SHIP_ACCELERATION = 300  # pixels per second squared
SHIP_FRICTION = 0.92  # velocity retained each frame
AUTOPILOT_SPEED = 120  # pixels per second when auto moving
PLANET_LANDING_SPEED = 100  # slower speed when approaching a planet

# --- Explorer/Boat movement -------------------------------------------------
EXPLORER_SPEED = 150  # base walking speed on a planet surface
BOAT_SPEED_LAND = 60  # slow boat speed when on land
BOAT_SPEED_WATER = 200  # slightly faster than walking when on water

ORBIT_SPEED_FACTOR = 0.005  # base factor used to calculate orbital speed

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
BLACKHOLE_RANGE = 300         # distance at which the ship feels the pull
BLACKHOLE_STRENGTH = 40000    # acceleration force applied when near
BLACKHOLE_RADIUS = 25         # radius of the dangerous core

# Worm hole settings
WORMHOLE_CHANCE = 0.05       # probability of a sector containing a wormhole pair
WORMHOLE_MIN_DISTANCE = 400  # minimum distance from star systems and black holes
WORMHOLE_RADIUS = 20         # visible size of a worm hole
WORMHOLE_COLOR = (150, 100, 200)
WORMHOLE_DELAY = 5.0         # seconds before teleport occurs
WORMHOLE_COOLDOWN = 3.0      # delay after teleport before re-entry allowed
WORMHOLE_FLASH_TIME = 0.75   # duration of post-teleport flash effect

# Enemy spawn settings
MIN_ENEMIES = 5
MAX_ENEMIES = 12
