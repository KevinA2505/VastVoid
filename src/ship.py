import pygame
import math
from dataclasses import dataclass
import config
import control_settings as controls
from fraction import Fraction
from planet import Planet
from names import get_ship_name
from combat import (
    Weapon,
    Projectile,
    Shield,
    LaserBeam,
    TimedMine,
    Drone,
    BombDrone,
    MissileWeapon,
    IonSymbiontShot,
    SlowField,
    SporeCloud,
)
from light_channeler import Channeler, Battery, StarTurret
from artifact import (
    Artifact,
    AreaShieldAura,
    EMPWave,
    TractorProbe,
    RepairNanobots,
    SolarLink,
    Decoy,
)
from blackhole import TemporaryBlackHole


@dataclass
class ShipModel:
    """Template describing a type of ship."""

    classification: str
    brand: str
    size: int
    color: tuple[int, int, int]
    accel_factor: float = 1.0


# Some predefined ship models used during character creation
SHIP_MODELS = [
    ShipModel("Fighter", "AeroTech", 18, (200, 200, 255), 1.2),
    ShipModel("Explorer", "NovaCorp", 20, (255, 220, 150), 1.0),
    ShipModel("Freighter", "Galactic Haul", 24, (180, 180, 180), 0.8),
    ShipModel("Interceptor", "Starlight", 16, (255, 100, 100), 1.4),
    ShipModel("Corvette", "ReconX", 17, (180, 220, 255), 1.5),
    ShipModel("Medical Frigate", "MediFleet", 22, (220, 255, 220), 0.9),
    ShipModel("Colony Transport", "Nexus", 26, (245, 210, 180), 0.7),
    ShipModel("Diplomatic Cruiser", "UnityWorks", 25, (240, 200, 255), 0.95),
    ShipModel("Automated Miner", "OreBots", 23, (200, 200, 150), 0.85),
    ShipModel("Research Vessel", "QuasarLabs", 21, (255, 245, 170), 1.0),
    ShipModel("Drone Carrier", "Vanguard", 19, (190, 230, 210), 1.1),
    ShipModel("Support Destroyer", "Bulwark", 23, (230, 190, 190), 0.9),
    ShipModel("Stealth Ship", "ShadowTech", 18, (100, 100, 100), 1.4),
    ShipModel("Mobile Workshop", "FixIt", 22, (200, 190, 180), 0.8),
]


class _ShipParticle:
    """Simple exhaust particle emitted by a ship."""

    def __init__(self, x: float, y: float, vx: float, vy: float) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = config.SHIP_PARTICLE_COLOR
        self.lifetime = config.SHIP_PARTICLE_DURATION
        # Store starting lifetime so we can fade the particle out over time
        self.max_life = config.SHIP_PARTICLE_DURATION

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt

    def expired(self) -> bool:
        return self.lifetime <= 0

class Ship:
    """Simple controllable ship with optional model attributes."""

    def __init__(
        self,
        x: float,
        y: float,
        model: ShipModel | None = None,
        hull: int = 100,
        speed_factor: float = 1.0,
        fraction: Fraction | None = None,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.autopilot_target = None
        self.orbit_target = None
        self.orbit_time = 0.0
        self.orbit_radius = 0.0
        self.orbit_angle = 0.0
        self.speed_factor = speed_factor
        self.orbit_speed = config.SHIP_ORBIT_SPEED * self.speed_factor
        self.orbit_fire_timer = 0.0
        self.orbit_cooldown = 0.0
        self.orbit_forced = False
        self.hyperjump_target: tuple[float, float] | None = None
        self.hyperjump_timer = 0.0
        self.hyperjump_cooldown = 0.0
        self.hyperjump_anim_time = 0.0
        self.hyperjump_elapsed = 0.0
        self._hyperjump_start = (0.0, 0.0)
        self.boost_charge = 1.0
        self.boost_time = 0.0
        self.model = model
        self.name = get_ship_name()
        self.fraction = fraction
        self.weapons: list[Weapon] = [Weapon("Laser", 8, 400)]
        self.active_weapon: int = 0
        for w in self.weapons:
            w.owner = self
        self.projectiles: list[Projectile] = []
        self.specials: list = []
        self.particles: list[_ShipParticle] = []
        self._structures: list | None = None
        self.shield = Shield()
        self.artifacts: list[Artifact] = []
        self.area_shield: AreaShieldAura | None = None
        # Crew handling
        self.pilot = None
        self.passengers: list = []
        self.hull = hull
        self.max_hull = hull
        self.invisible_timer = 0.0
        if model:
            self.brand = model.brand
            self.classification = model.classification
            self.size = model.size
            self.color = model.color
            self.accel_factor = model.accel_factor
        else:
            self.brand = "Generic"
            self.classification = "Standard"
            self.size = config.SHIP_SIZE
            self.color = config.SHIP_COLOR
            self.accel_factor = 1.0
        # Orientation angle in radians. 0 points to the right.
        self.angle = -math.pi / 2
        # Collision radius for the triangular hull
        height = self.size * 1.5
        self.collision_radius = math.hypot(height / 2, self.size / 2)

    def set_active_weapon(self, index: int) -> None:
        if 0 <= index < len(self.weapons):
            self.active_weapon = index

    def assign_pilot(self, member) -> None:
        """Assign a crew member as pilot of this ship."""
        self.pilot = member

    def remove_pilot(self) -> None:
        """Remove the current pilot if any."""
        self.pilot = None

    def add_passenger(self, member) -> None:
        """Add a passenger if space allows (max two)."""
        if member not in self.passengers and len(self.passengers) < 2:
            self.passengers.append(member)

    def remove_passenger(self, member) -> None:
        """Remove ``member`` from passengers if present."""
        if member in self.passengers:
            self.passengers.remove(member)

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
        targets: list | None = None,
        structures: list | None = None,
    ) -> None:
        self._structures = list(structures or [])
        # Include any active drones launched from capital ships or other
        # structures so they can participate in collision checks.
        for struct in structures or []:
            for dr in getattr(struct, "drones", []):
                self._structures.append(dr)
        self._sectors = sectors
        self._update_particles(dt)
        if self.invisible_timer > 0:
            self.invisible_timer = max(0.0, self.invisible_timer - dt)
        if self.orbit_cooldown > 0:
            self.orbit_cooldown = max(0.0, self.orbit_cooldown - dt)
        if self.hyperjump_cooldown > 0:
            self.hyperjump_cooldown = max(0.0, self.hyperjump_cooldown - dt)

        # Always recharge shields and update weapon timers
        self.shield.recharge(dt)
        for weapon in self.weapons:
            weapon.update(dt)
        for art in self.artifacts:
            art.update(dt)

        if self.pilot and self._update_hyperjump(
            dt, world_width, world_height, targets
        ):
            return

        if self.orbit_time > 0 and self.orbit_target:
            self._update_orbit(dt)
            self._update_projectiles(dt, world_width, world_height)
            self._update_specials(dt, world_width, world_height, targets)
            if self.boost_time > 0 and self.orbit_forced:
                self.cancel_orbit()
            return

        if self.pilot and self.autopilot_target:
            self._update_autopilot(
                dt, world_width, world_height, sectors, blackholes
            )
            return

        if self.pilot:
            accel = (
                config.SHIP_ACCELERATION * self.accel_factor * self.speed_factor
            )
            if self.boost_time > 0:
                self.boost_time -= dt
                if self.boost_time <= 0:
                    self.boost_time = 0
            else:
                if self.boost_charge < 1.0:
                    self.boost_charge = min(
                        1.0, self.boost_charge + dt / config.BOOST_RECHARGE
                    )
                if keys[controls.get_key("boost")] and self.boost_charge >= 1.0:
                    self.boost_time = config.BOOST_DURATION
                    self.boost_charge = 0.0
            if self.boost_time > 0:
                accel *= config.BOOST_MULTIPLIER

            if keys[controls.get_key("move_up")]:
                self.vy -= accel * dt
            if keys[controls.get_key("move_down")]:
                self.vy += accel * dt
            if keys[controls.get_key("move_left")]:
                self.vx -= accel * dt
            if keys[controls.get_key("move_right")]:
                self.vx += accel * dt

            self.vx *= config.SHIP_FRICTION
            self.vy *= config.SHIP_FRICTION

            # Clamp velocity to a moderate maximum so all ships travel evenly
            speed_limit = config.SHIP_MAX_SPEED * self.speed_factor
            if self.boost_time > 0:
                speed_limit *= config.BOOST_MULTIPLIER
            vel = math.hypot(self.vx, self.vy)
            if vel > speed_limit:
                scale = speed_limit / vel
                self.vx *= scale
                self.vy *= scale

            if abs(self.vx) > 1e-3 or abs(self.vy) > 1e-3:
                self.angle = math.atan2(self.vy, self.vx)
                if abs(self.vx) > 40 or abs(self.vy) > 40:
                    self._emit_particle()

            if blackholes:
                for hole in blackholes:
                    hole.apply_pull(self, dt)

            old_x, old_y = self.x, self.y

            self.x += self.vx * dt
            self.y += self.vy * dt

            self.x = max(0, min(world_width, self.x))
            self.y = max(0, min(world_height, self.y))

            if self._check_collision(sectors):
                self.x, self.y = old_x, old_y
                self.vx *= -config.BOUNCE_FACTOR
                self.vy *= -config.BOUNCE_FACTOR
                # Nudge slightly away from the obstacle
                self.x += self.vx * dt
                self.y += self.vy * dt

        self._update_projectiles(dt, world_width, world_height)
        self._update_specials(dt, world_width, world_height, targets)

    def start_autopilot(self, target) -> None:
        if not self.pilot:
            return
        self.autopilot_target = target

    def cancel_autopilot(self) -> None:
        self.autopilot_target = None

    def start_hyperjump(self, x: float, y: float) -> None:
        """Initiate a hyperjump to the given coordinates."""
        if not self.pilot:
            return
        if (
            self.hyperjump_cooldown > 0
            or self.hyperjump_timer > 0
            or self.hyperjump_target is not None
        ):
            return
        self.hyperjump_target = (float(x), float(y))
        self.hyperjump_timer = config.HYPERJUMP_DELAY
        # Face the ship toward its destination
        self.angle = math.atan2(y - self.y, x - self.x)
        dist = math.hypot(x - self.x, y - self.y)
        d_pc = dist / config.HYPERJUMP_UNIT
        v = config.HYPERJUMP_BASE_SPEED * (
            1 + config.HYPERJUMP_SPEED_SCALE * math.log10(1 + d_pc / config.HYPERJUMP_D0)
        )
        self.hyperjump_anim_time = d_pc / v if v > 0 else 0.0
        self.hyperjump_anim_time = max(
            config.HYPERJUMP_MIN_TIME,
            min(self.hyperjump_anim_time, config.HYPERJUMP_MAX_TIME),
        )
        self.hyperjump_elapsed = 0.0
        self._hyperjump_start = (self.x, self.y)
        self.autopilot_target = None
        self.cancel_orbit()

    def start_orbit(
        self,
        target,
        duration: float = 5.0,
        forced: bool = False,
        speed: float | None = None,
    ) -> None:
        """Begin orbiting ``target`` for a short duration."""
        if self.orbit_cooldown > 0 or self.orbit_time > 0:
            return
        dx = self.x - target.x
        dy = self.y - target.y
        self.orbit_radius = math.hypot(dx, dy)
        self.orbit_angle = math.atan2(dy, dx)
        self.orbit_target = target
        self.orbit_time = duration
        self.orbit_forced = forced
        base_speed = speed if speed is not None else config.SHIP_ORBIT_SPEED
        self.orbit_speed = base_speed * self.speed_factor
        self.orbit_fire_timer = 0.0
        self.autopilot_target = None

    def cancel_orbit(self) -> None:
        self.orbit_target = None
        self.orbit_time = 0.0
        self.orbit_forced = False
        self.orbit_speed = config.SHIP_ORBIT_SPEED * self.speed_factor
        self.orbit_fire_timer = 0.0
        self.orbit_cooldown = config.ORBIT_COOLDOWN

    def _update_hyperjump(
        self,
        dt: float,
        world_width: int,
        world_height: int,
        targets: list | None = None,
    ) -> bool:
        """Handle hyperjump countdown and teleportation."""
        if self.hyperjump_timer > 0:
            self.hyperjump_timer -= dt
            self.vx = 0.0
            self.vy = 0.0
            self._update_projectiles(dt, world_width, world_height)
            self._update_specials(dt, world_width, world_height, targets)
            return True

        if self.hyperjump_target is not None:
            self.hyperjump_elapsed += dt
            t = (
                self.hyperjump_elapsed / self.hyperjump_anim_time
                if self.hyperjump_anim_time > 0
                else 1.0
            )
            t = min(1.0, t)
            self.x = (1 - t) * self._hyperjump_start[0] + t * self.hyperjump_target[0]
            self.y = (1 - t) * self._hyperjump_start[1] + t * self.hyperjump_target[1]
            self.vx = 0.0
            self.vy = 0.0
            self._update_projectiles(dt, world_width, world_height)
            self._update_specials(dt, world_width, world_height, targets)
            if t >= 1.0:
                self.hyperjump_target = None
                self.hyperjump_cooldown = config.HYPERJUMP_COOLDOWN
            return True

        return False

    def _update_autopilot(
        self,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
    ) -> None:
        dest_x, dest_y = self.autopilot_target.x, self.autopilot_target.y
        dx = dest_x - self.x
        dy = dest_y - self.y
        distance = math.hypot(dx, dy)
        speed_limit = config.AUTOPILOT_SPEED * self.speed_factor
        if isinstance(self.autopilot_target, Planet):
            speed_limit = config.PLANET_LANDING_SPEED * self.speed_factor
        step = speed_limit * dt
        if distance <= step:
            self.x = dest_x
            self.y = dest_y
            self.autopilot_target = None
            self.vx = 0.0
            self.vy = 0.0
            return

        angle = math.atan2(dy, dx)
        accel = config.SHIP_ACCELERATION * self.accel_factor * self.speed_factor
        self.vx += math.cos(angle) * accel * dt
        self.vy += math.sin(angle) * accel * dt
        vel = math.hypot(self.vx, self.vy)
        if vel > speed_limit:
            scale = speed_limit / vel
            self.vx *= scale
            self.vy *= scale

        self.vx *= config.SHIP_FRICTION
        self.vy *= config.SHIP_FRICTION

        self.angle = math.atan2(self.vy, self.vx)
        old_x, old_y = self.x, self.y
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = max(0, min(world_width, self.x))
        self.y = max(0, min(world_height, self.y))
        self._emit_particle()

        if blackholes:
            for hole in blackholes:
                hole.apply_pull(self, dt)
                self.x += self.vx * dt
                self.y += self.vy * dt

        if self._check_collision(sectors):
            self.x, self.y = old_x, old_y
            self.vx *= -config.BOUNCE_FACTOR
            self.vy *= -config.BOUNCE_FACTOR
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.autopilot_target = None

        self._update_projectiles(dt, world_width, world_height)

    def _update_orbit(self, dt: float) -> None:
        if not self.orbit_target:
            return
        self.orbit_time -= dt
        self.orbit_angle += self.orbit_speed * dt
        self.x = self.orbit_target.x + math.cos(self.orbit_angle) * self.orbit_radius
        self.y = self.orbit_target.y + math.sin(self.orbit_angle) * self.orbit_radius
        self.angle = self.orbit_angle + math.pi / 2
        self._emit_particle()
        self.orbit_fire_timer -= dt
        if self.orbit_fire_timer <= 0:
            # Fire a homing projectile while orbiting
            if self.weapons:
                weapon = self.weapons[0]
                if weapon.can_fire():
                    proj = weapon.fire_homing(self.x, self.y, self.orbit_target)
                    if proj:
                        proj.vx *= config.ORBIT_PROJECTILE_SPEED_MULTIPLIER
                        proj.vy *= config.ORBIT_PROJECTILE_SPEED_MULTIPLIER
                        self.projectiles.append(proj)
            self.orbit_fire_timer += 1.0
        if self.orbit_time <= 0:
            self.cancel_orbit()

    def _predict_target_position(self, target, speed: float) -> tuple[float, float]:
        """Return an estimated future position for ``target`` given projectile speed."""
        dx = target.x - self.x
        dy = target.y - self.y
        dvx = target.vx
        dvy = target.vy
        a = dvx * dvx + dvy * dvy - speed * speed
        b = 2 * (dx * dvx + dy * dvy)
        c = dx * dx + dy * dy
        t = 0.0
        disc = b * b - 4 * a * c
        if abs(a) < 1e-6 or disc < 0:
            if speed > 0:
                t = math.sqrt(c) / speed
        else:
            sqrt_disc = math.sqrt(disc)
            t1 = (-b + sqrt_disc) / (2 * a)
            t2 = (-b - sqrt_disc) / (2 * a)
            t_candidates = [val for val in (t1, t2) if val > 0]
            if t_candidates:
                t = min(t_candidates)
        return target.x + dvx * t, target.y + dvy * t

    def _check_collision(self, sectors: list) -> bool:
        radius = self.collision_radius
        for sector in sectors:
            if sector.collides_with_point(self.x, self.y, radius):
                return True
        for struct in self._structures:
            # Skip small drones so they don't trap the player when colliding.
            if isinstance(struct, Drone):
                continue
            if struct is self:
                continue
            # Drones only provide ``size`` representing their collision radius,
            # while larger structures expose a ``radius`` attribute. Handle both
            # so ships properly avoid them.
            if hasattr(struct, "radius"):
                struct_radius = struct.radius
            else:
                struct_radius = getattr(struct, "size", 0)
            if math.hypot(struct.x - self.x, struct.y - self.y) < radius + struct_radius:
                return True
        return False

    def _structure_collision(self, x: float, y: float, r: float = 0) -> bool:
        """Return ``True`` if the point overlaps any stationary structure."""
        for sector in getattr(self, "_sectors", []):
            if sector.collides_with_point(x, y, r):
                return True

        for struct in self._structures:
            if isinstance(struct, (Ship, Drone)):
                continue
            if hasattr(struct, "collides_with_point"):
                if struct.collides_with_point(x, y, r):
                    return True
            else:
                sr = getattr(struct, "radius", getattr(struct, "size", 0))
                if sr and math.hypot(struct.x - x, struct.y - y) < sr + r:
                    return True
        return False

    def _triangle_points(self, cx: float, cy: float, zoom: float) -> list[tuple[int, int]]:
        """Return the three rotated vertices of the ship."""
        base = self.size * zoom
        height = self.size * 1.5 * zoom
        hx = height / 2
        half_base = base / 2
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        tip = (cx + cos_a * hx, cy + sin_a * hx)
        left = (
            cx - cos_a * hx - sin_a * half_base,
            cy - sin_a * hx + cos_a * half_base,
        )
        right = (
            cx - cos_a * hx + sin_a * half_base,
            cy - sin_a * hx - cos_a * half_base,
        )
        return [(int(tip[0]), int(tip[1])), (int(left[0]), int(left[1])), (int(right[0]), int(right[1]))]

    def _draw_hyperjump_trail(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        """Render the bright trail from the jump origin to the ship."""
        if not self.hyperjump_active:
            return
        sx, sy = self._hyperjump_start
        start = (int((sx - offset_x) * zoom), int((sy - offset_y) * zoom))
        end = (int((self.x - offset_x) * zoom), int((self.y - offset_y) * zoom))
        width = max(1, int(config.HYPERJUMP_TRAIL_WIDTH * zoom))
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        if self.hyperjump_target is not None and self.hyperjump_anim_time > 0:
            t = self.hyperjump_elapsed / self.hyperjump_anim_time
            t = min(1.0, max(0.0, t))
        else:
            t = 0.0
        outer_alpha = int(180 * (1.0 - t))
        inner_alpha = int(220 * (1.0 - t))
        pygame.draw.line(
            surf,
            config.HYPERJUMP_TRAIL_COLOR + (outer_alpha,),
            start,
            end,
            width,
        )
        pygame.draw.line(
            surf,
            config.HYPERJUMP_TRAIL_INNER_COLOR + (inner_alpha,),
            start,
            end,
            max(1, width // 2),
        )
        screen.blit(surf, (0, 0))

    def _draw_hyperjump_shock(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        """Render a short shock cone when entering hyperspace."""
        if not self.hyperjump_active:
            return
        intensity = 0.0
        if self.hyperjump_timer > 0:
            intensity = 1.0 - self.hyperjump_timer / config.HYPERJUMP_DELAY
        elif self.hyperjump_target is not None and self.hyperjump_anim_time > 0:
            t = self.hyperjump_elapsed / self.hyperjump_anim_time
            t = min(1.0, t)
            intensity = 1.0 - t
        if intensity <= 0.0:
            return
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        length = self.size * 3 * zoom
        width = self.size * 1.5 * zoom
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        tip = (cx + cos_a * length, cy + sin_a * length)
        left = (cx - sin_a * width / 2, cy + cos_a * width / 2)
        right = (cx + sin_a * width / 2, cy - cos_a * width / 2)
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        color = config.HYPERJUMP_SHOCK_COLOR + (int(150 * intensity),)
        pygame.draw.polygon(surf, color, [left, tip, right])
        screen.blit(surf, (0, 0))

    def draw(
        self,
        screen: pygame.Surface,
        zoom: float = 1.0,
        player_fraction: Fraction | None = None,
        aura_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw the ship scaled by a non-linear factor of the zoom level."""
        cx = config.WINDOW_WIDTH // 2
        cy = config.WINDOW_HEIGHT // 2
        offset_x = self.x - cx / zoom
        offset_y = self.y - cy / zoom
        self._draw_hyperjump_shock(screen, offset_x, offset_y, zoom)
        self._draw_hyperjump_trail(screen, offset_x, offset_y, zoom)
        self.draw_particles(screen, offset_x, offset_y, zoom)
        points = self._triangle_points(cx, cy, zoom)
        pygame.draw.polygon(screen, self.color, points)
        if (
            player_fraction
            and self.fraction
            and self.fraction == player_fraction
        ):
            r = int(self.collision_radius * zoom * 1.4)
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            color = aura_color or (
                self.fraction.color if self.fraction else self.color
            )
            pygame.draw.circle(aura, color + (80,), (r, r), r)
            screen.blit(aura, (cx - r, cy - r))

    @property
    def boost_ratio(self) -> float:
        """Return current boost charge as a 0-1 ratio."""
        if self.boost_time > 0:
            return 0.0
        return self.boost_charge

    @property
    def hyperjump_active(self) -> bool:
        """Return ``True`` while a hyperjump animation is playing."""
        return self.hyperjump_timer > 0 or self.hyperjump_target is not None

    def fire(self, tx: float, ty: float) -> None:
        if self.pilot is None or not self.weapons:
            return
        weapon = self.weapons[self.active_weapon]
        proj = None
        if self.orbit_target and self.orbit_time > 0:
            target = self.orbit_target
            if weapon.can_fire():
                proj = weapon.fire_homing(self.x, self.y, target)
                if proj:
                    proj.vx *= config.ORBIT_PROJECTILE_SPEED_MULTIPLIER
                    proj.vy *= config.ORBIT_PROJECTILE_SPEED_MULTIPLIER
        else:
            proj = weapon.fire(self.x, self.y, tx, ty)
        if proj:
            if isinstance(
                proj,
                (
                    LaserBeam,
                    TimedMine,
                    Drone,
                    BombDrone,
                    IonSymbiontShot,
                    SlowField,
                    SporeCloud,
                    Channeler,
                    Battery,
                    StarTurret,
                ),
            ):
                self.specials.append(proj)
            else:
                self.projectiles.append(proj)

    def fire_homing(self, target) -> None:
        """Fire a homing projectile at ``target`` using the first weapon."""
        if not self.weapons:
            return
        weapon = self.weapons[self.active_weapon]
        proj = weapon.fire_homing(self.x, self.y, target)
        if proj:
            if isinstance(
                proj,
                (
                    LaserBeam,
                    TimedMine,
                    Drone,
                    BombDrone,
                    IonSymbiontShot,
                    SlowField,
                    SporeCloud,
                    Channeler,
                    Battery,
                    StarTurret,
                ),
            ):
                self.specials.append(proj)
            else:
                self.projectiles.append(proj)

    def start_weapon_charge(self) -> None:
        if not self.weapons:
            return
        weapon = self.weapons[self.active_weapon]
        if hasattr(weapon, "start_charging"):
            weapon.start_charging()

    def release_weapon_charge(self, tx: float, ty: float) -> None:
        if not self.weapons:
            return
        weapon = self.weapons[self.active_weapon]
        if hasattr(weapon, "release"):
            proj = weapon.release(self.x, self.y, tx, ty)
            if proj:
                if isinstance(
                    proj,
                    (
                        LaserBeam,
                        TimedMine,
                        Drone,
                        BombDrone,
                        IonSymbiontShot,
                        SlowField,
                        SporeCloud,
                        Channeler,
                        Battery,
                        StarTurret,
                    ),
                ):
                    self.specials.append(proj)
                else:
                    self.projectiles.append(proj)

    def use_artifact(self, index: int, targets: list) -> None:
        """Activate an equipped artifact if possible."""
        if 0 <= index < len(self.artifacts):
            art = self.artifacts[index]
            if art.can_use():
                art.activate(self, targets)

    def _update_projectiles(self, dt: float, world_width: int, world_height: int) -> None:
        for proj in list(self.projectiles):
            proj.update(dt)
            hit = self._structure_collision(
                proj.x,
                proj.y,
                getattr(proj, "radius", 0),
            )
            out_of_bounds = not (0 <= proj.x <= world_width and 0 <= proj.y <= world_height)
            if proj.expired() or out_of_bounds or hit:
                self.projectiles.remove(proj)

    def _update_particles(self, dt: float) -> None:
        for p in list(self.particles):
            p.update(dt)
            if p.expired():
                self.particles.remove(p)

    def _emit_particle(self) -> None:
        if len(self.particles) >= config.SHIP_PARTICLE_MAX:
            self.particles.pop(0)
        hx = self.size * 1.5 / 2
        px = self.x - math.cos(self.angle) * hx
        py = self.y - math.sin(self.angle) * hx
        speed = 60.0
        vx = self.vx - math.cos(self.angle) * speed
        vy = self.vy - math.sin(self.angle) * speed
        self.particles.append(_ShipParticle(px, py, vx, vy))

    def _update_specials(self, dt: float, world_width: int, world_height: int, targets: list | None = None) -> None:
        structures = list(self._structures or [])
        for obj in list(self.specials):
            if isinstance(obj, LaserBeam):
                obj.update(dt, (targets or []) + structures)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, TimedMine):
                obj.update(dt)
                if obj.exploded:
                    if targets:
                        for tar in targets:
                            if math.hypot(tar.ship.x - obj.x, tar.ship.y - obj.y) <= obj.radius:
                                tar.ship.take_damage(obj.damage)
                    for struct in structures:
                        sr = getattr(struct, "radius", getattr(struct, "size", 0))
                        if math.hypot(struct.x - obj.x, struct.y - obj.y) <= obj.radius + sr:
                            pass
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, Drone):
                obj.update(dt, (targets or []) + structures)
                for proj in list(obj.projectiles):
                    for tar in targets or []:
                        if (
                            math.hypot(proj.x - tar.ship.x, proj.y - tar.ship.y)
                            <= tar.ship.collision_radius
                        ):
                            tar.ship.take_damage(proj.damage)
                            obj.projectiles.remove(proj)
                            break
                    else:
                        for struct in structures:
                            sr = getattr(struct, "radius", getattr(struct, "size", 0))
                            if math.hypot(proj.x - struct.x, proj.y - struct.y) <= sr:
                                obj.projectiles.remove(proj)
                                break
                drone_rect = pygame.Rect(
                    obj.x - obj.size / 2,
                    obj.y - obj.size / 2,
                    obj.size,
                    obj.size,
                )
                for tar in targets or []:
                    for proj in list(tar.ship.projectiles):
                        if drone_rect.collidepoint(proj.x, proj.y):
                            obj.hp -= proj.damage
                            tar.ship.projectiles.remove(proj)
                            if obj.hp <= 0:
                                break
                for struct in structures:
                    for proj in list(getattr(struct, "projectiles", [])):
                        if drone_rect.collidepoint(proj.x, proj.y):
                            obj.hp -= getattr(proj, "damage", 0)
                            getattr(struct, "projectiles").remove(proj)
                            if obj.hp <= 0:
                                break
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, BombDrone):
                obj.update(dt, (targets or []) + structures)
                bomb_rect = pygame.Rect(
                    obj.x - obj.size / 2,
                    obj.y - obj.size / 2,
                    obj.size,
                    obj.size,
                )
                hit = False
                for tar in targets or []:
                    for proj in list(tar.ship.projectiles):
                        if bomb_rect.collidepoint(proj.x, proj.y):
                            obj.hp -= proj.damage
                            tar.ship.projectiles.remove(proj)
                            if obj.hp <= 0:
                                hit = True
                                break
                    if hit:
                        break
                    if (
                        math.hypot(tar.ship.x - obj.x, tar.ship.y - obj.y)
                        <= tar.ship.collision_radius
                    ):
                        hit = True
                        break
                if not hit:
                    for struct in structures:
                        for proj in list(getattr(struct, "projectiles", [])):
                            if bomb_rect.collidepoint(proj.x, proj.y):
                                obj.hp -= getattr(proj, "damage", 0)
                                getattr(struct, "projectiles").remove(proj)
                                if obj.hp <= 0:
                                    hit = True
                                    break
                        if hit:
                            break
                        sr = getattr(struct, "radius", getattr(struct, "size", 0))
                        if math.hypot(struct.x - obj.x, struct.y - obj.y) <= sr:
                            hit = True
                            break
                if hit:
                    obj._explode()
                if obj.exploded:
                    if targets:
                        for tar in targets:
                            if math.hypot(tar.ship.x - obj.x, tar.ship.y - obj.y) <= obj.radius:
                                tar.ship.take_damage(obj.damage)
                    for struct in structures:
                        sr = getattr(struct, "radius", getattr(struct, "size", 0))
                        if math.hypot(struct.x - obj.x, struct.y - obj.y) <= obj.radius + sr:
                            pass
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, IonSymbiontShot):
                obj.update(dt, targets or [])
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, SlowField):
                obj.update(dt)
                for tar in targets or []:
                    obj.apply_slow(tar.ship)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, SporeCloud):
                tick = obj.update(dt)
                for struct in structures:
                    if obj.contains(struct):
                        sr = getattr(struct, "radius", getattr(struct, "size", 0))
                        dist = math.hypot(struct.x - obj.x, struct.y - obj.y) - sr
                        if dist <= 0:
                            self.specials.remove(obj)
                            break
                        obj.radius = min(obj.radius, dist)
                else:
                    if tick:
                        for tar in targets or []:
                            if obj.contains(tar.ship):
                                tar.ship.take_damage(obj.damage)
                    if obj.expired():
                        self.specials.remove(obj)
            elif isinstance(obj, EMPWave):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, TractorProbe):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, TemporaryBlackHole):
                obj.update(dt)
                obj.apply_pull(self, dt)
                for tar in targets or []:
                    obj.apply_pull(tar.ship, dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, AreaShieldAura):
                # Intercept incoming projectiles while the aura holds
                for tar in targets or []:
                    for proj in list(tar.ship.projectiles):
                        if math.hypot(proj.x - self.x, proj.y - self.y) <= obj.radius:
                            obj.take_damage(proj.damage)
                            tar.ship.projectiles.remove(proj)
                if obj.expired():
                    self.area_shield = None
                    self.specials.remove(obj)
            elif isinstance(obj, RepairNanobots):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, SolarLink):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, Decoy):
                obj.update(dt, targets or [])
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, Channeler):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, Battery):
                obj.update(dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, StarTurret):
                obj.update(dt, targets or [])
                for sc in list(obj.projectiles):
                    if sc.expired():
                        obj.projectiles.remove(sc)
                if obj.expired():
                    self.specials.remove(obj)

    def take_damage(self, amount: float) -> None:
        """Apply damage to the shield and hull."""
        if self.invisible_timer > 0:
            return
        if self.area_shield and self.area_shield.strength > 0:
            self.area_shield.take_damage(amount)
            if self.area_shield.expired():
                self.specials.remove(self.area_shield)
                self.area_shield = None
            return
        if self.shield.strength > 0:
            before = self.shield.strength
            self.shield.take_damage(amount)
            overflow = amount - before
            if overflow > 0:
                self.hull = max(0, self.hull - overflow)
        else:
            self.hull = max(0, self.hull - amount)

    def draw_projectiles(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        for proj in self.projectiles:
            proj.draw(screen, offset_x, offset_y, zoom)

    def draw_specials(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        for obj in self.specials:
            if isinstance(obj, Drone):
                for proj in obj.projectiles:
                    proj.draw(screen, offset_x, offset_y, zoom)
            elif isinstance(obj, StarTurret):
                for sc in obj.projectiles:
                    sc.draw(screen, offset_x, offset_y, zoom)
            obj.draw(screen, offset_x, offset_y, zoom)
        if self.area_shield:
            self.area_shield.draw(screen, offset_x, offset_y, zoom)

    def draw_particles(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        for p in self.particles:
            px = int((p.x - offset_x) * zoom)
            py = int((p.y - offset_y) * zoom)
            # Fade out by scaling alpha with remaining life
            alpha = max(0.0, min(1.0, p.lifetime / p.max_life))
            radius = max(1, int(2 * alpha * zoom))
            surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, p.color + (int(alpha * 255),), (radius, radius), radius)
            screen.blit(surface, (px - radius, py - radius))

    def draw_at(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
        player_fraction: Fraction | None = None,
        aura_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw the ship on screen applying an offset and zoom."""
        if self.invisible_timer > 0:
            return
        self._draw_hyperjump_shock(screen, offset_x, offset_y, zoom)
        self._draw_hyperjump_trail(screen, offset_x, offset_y, zoom)
        self.draw_particles(screen, offset_x, offset_y, zoom)
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        points = self._triangle_points(cx, cy, zoom)
        pygame.draw.polygon(screen, self.color, points)
        if (
            player_fraction
            and self.fraction
            and self.fraction == player_fraction
        ):
            r = int(self.collision_radius * zoom * 1.4)
            aura = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            color = aura_color or (
                self.fraction.color if self.fraction else self.color
            )
            pygame.draw.circle(aura, color + (80,), (r, r), r)
            screen.blit(aura, (cx - r, cy - r))


def choose_ship(screen: pygame.Surface) -> ShipModel:
    """Let the player select a ship model and return it."""
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.unicode.isdigit():
                idx = int(event.unicode) - 1
                if 0 <= idx < len(SHIP_MODELS):
                    return SHIP_MODELS[idx]
        screen.fill(config.BACKGROUND_COLOR)
        lines = ["Choose your ship:"]
        for i, model in enumerate(SHIP_MODELS):
            lines.append(
                f"{i+1} - {model.brand} {model.classification}"
            )
        for i, line in enumerate(lines):
            msg = font.render(line, True, (255, 255, 255))
            screen.blit(msg, (50, 100 + i * 30))
        pygame.display.flip()
        clock.tick(30)
