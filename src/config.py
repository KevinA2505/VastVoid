WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 20)  # near black

SHIP_COLOR = (255, 255, 255)
SHIP_SIZE = 20
SHIP_ACCELERATION = 300  # pixels per second squared
SHIP_FRICTION = 0.92  # velocity retained each frame
AUTOPILOT_SPEED = 200  # pixels per second when auto moving

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
