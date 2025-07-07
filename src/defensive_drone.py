import math
import pygame
import config


class DefensiveDrone:
    """Simple defensive drone that orbits its owner and intercepts threats."""

    def __init__(
        self,
        owner,
        angle: float = 0.0,
        orbit_radius: float | None = None,
        orbit_speed: float = config.DEF_DRONE_ORBIT_SPEED,
        hp: float = 20.0,
        speed_factor: float = 1.0,
    ) -> None:
        self.owner = owner
        self.angle = angle
        self.orbit_speed = orbit_speed * speed_factor
        self.orbit_radius = (
            orbit_radius or owner.size * config.DEF_DRONE_ORBIT_RADIUS_FACTOR
        )
        self.intercept_speed = config.DEF_DRONE_INTERCEPT_SPEED * speed_factor
        self.hp = hp
        self.size = 12
        self.x = owner.x + math.cos(angle) * self.orbit_radius
        self.y = owner.y + math.sin(angle) * self.orbit_radius
        self.state = "idle"
        self.target = None

    def _find_threat(self, objects: list) -> object | None:
        detection = config.DEF_DRONE_DETECTION_RANGE
        for obj in objects:
            dist = math.hypot(obj.ship.x - self.owner.x, obj.ship.y - self.owner.y)
            if dist <= detection:
                return obj.ship
            for proj in obj.ship.projectiles:
                d = math.hypot(proj.x - self.owner.x, proj.y - self.owner.y)
                if d <= detection:
                    return proj
        return None

    def update(self, dt: float, objects: list) -> None:
        if self.state == "idle":
            self.angle += self.orbit_speed * dt
            self.x = self.owner.x + math.cos(self.angle) * self.orbit_radius
            self.y = self.owner.y + math.sin(self.angle) * self.orbit_radius
            threat = self._find_threat(objects)
            if threat:
                self.target = threat
                self.state = "intercept"
        else:
            if isinstance(self.target, object):
                tx = getattr(self.target, "x", self.owner.x)
                ty = getattr(self.target, "y", self.owner.y)
                target_size = getattr(self.target, "size", 0)
            else:
                tx, ty = self.owner.x, self.owner.y
                target_size = 0
            dx = tx - self.x
            dy = ty - self.y
            dist = math.hypot(dx, dy) or 1.0
            self.x += (dx / dist * self.intercept_speed) * dt
            self.y += (dy / dist * self.intercept_speed) * dt
            safe = (self.size + target_size) * 0.5
            if dist <= safe:
                self.state = "idle"
                self.target = None
        max_dist = self.orbit_radius * config.DEF_DRONE_MAX_ROAM_FACTOR
        d_from_owner = math.hypot(self.x - self.owner.x, self.y - self.owner.y)
        if d_from_owner > max_dist:
            angle = math.atan2(self.y - self.owner.y, self.x - self.owner.x)
            self.x = self.owner.x + math.cos(angle) * max_dist
            self.y = self.owner.y + math.sin(angle) * max_dist

    def expired(self) -> bool:
        return self.hp <= 0

    def draw(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        pos = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        pygame.draw.circle(screen, (100, 180, 255), pos, max(2, int(5 * zoom)))
