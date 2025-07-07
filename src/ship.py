import pygame
import math
from dataclasses import dataclass
import config
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
)
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
        self.orbit_speed = config.SHIP_ORBIT_SPEED
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
        self.weapons: list[Weapon] = [Weapon("Laser", 8, 400)]
        self.active_weapon: int = 0
        for w in self.weapons:
            w.owner = self
        self.projectiles: list[Projectile] = []
        self.specials: list = []
        self.particles: list[_ShipParticle] = []
        self._enemy_list: list | None = None
        self._structures: list | None = None
        self.shield = Shield()
        self.artifacts: list[Artifact] = []
        self.area_shield: AreaShieldAura | None = None
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

    def update(
        self,
        keys: pygame.key.ScancodeWrapper,
        dt: float,
        world_width: int,
        world_height: int,
        sectors: list,
        blackholes: list | None = None,
        enemies: list | None = None,
        structures: list | None = None,
    ) -> None:
        self._enemy_list = enemies
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
        if self._update_hyperjump(dt, world_width, world_height, enemies):
            return

        # Always recharge shields and update weapon timers
        self.shield.recharge(dt)
        for weapon in self.weapons:
            weapon.update(dt)
        for art in self.artifacts:
            art.update(dt)

        if self.orbit_time > 0 and self.orbit_target:
            self._update_orbit(dt)
            self._update_projectiles(dt, world_width, world_height)
            self._update_specials(dt, world_width, world_height, enemies)
            if self.boost_time > 0 and self.orbit_forced:
                self.cancel_orbit()
            return

        if self.autopilot_target:
            self._update_autopilot(dt, world_width, world_height, sectors, blackholes)
            return

        accel = config.SHIP_ACCELERATION * self.accel_factor
        if self.boost_time > 0:
            self.boost_time -= dt
            if self.boost_time <= 0:
                self.boost_time = 0
        else:
            if self.boost_charge < 1.0:
                self.boost_charge = min(1.0, self.boost_charge + dt / config.BOOST_RECHARGE)
            if keys[pygame.K_LSHIFT] and self.boost_charge >= 1.0:
                self.boost_time = config.BOOST_DURATION
                self.boost_charge = 0.0
        if self.boost_time > 0:
            accel *= config.BOOST_MULTIPLIER

        if keys[pygame.K_w]:
            self.vy -= accel * dt
        if keys[pygame.K_s]:
            self.vy += accel * dt
        if keys[pygame.K_a]:
            self.vx -= accel * dt
        if keys[pygame.K_d]:
            self.vx += accel * dt

        self.vx *= config.SHIP_FRICTION
        self.vy *= config.SHIP_FRICTION

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
            self.vx = 0
            self.vy = 0

        self._update_projectiles(dt, world_width, world_height)
        self._update_specials(dt, world_width, world_height, enemies)

    def start_autopilot(self, target) -> None:
        self.autopilot_target = target

    def cancel_autopilot(self) -> None:
        self.autopilot_target = None

    def start_hyperjump(self, x: float, y: float) -> None:
        """Initiate a hyperjump to the given coordinates."""
        if (
            self.hyperjump_cooldown > 0
            or self.hyperjump_timer > 0
            or self.hyperjump_target is not None
        ):
            return
        self.hyperjump_target = (float(x), float(y))
        self.hyperjump_timer = config.HYPERJUMP_DELAY
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
        self.orbit_speed = speed if speed is not None else config.SHIP_ORBIT_SPEED
        self.orbit_fire_timer = 0.0
        self.autopilot_target = None

    def cancel_orbit(self) -> None:
        self.orbit_target = None
        self.orbit_time = 0.0
        self.orbit_forced = False
        self.orbit_speed = config.SHIP_ORBIT_SPEED
        self.orbit_fire_timer = 0.0
        self.orbit_cooldown = config.ORBIT_COOLDOWN

    def _update_hyperjump(
        self,
        dt: float,
        world_width: int,
        world_height: int,
        enemies: list | None = None,
    ) -> bool:
        """Handle hyperjump countdown and teleportation."""
        if self.hyperjump_timer > 0:
            self.hyperjump_timer -= dt
            self.vx = 0.0
            self.vy = 0.0
            self._update_projectiles(dt, world_width, world_height)
            self._update_specials(dt, world_width, world_height, enemies)
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
            self._update_specials(dt, world_width, world_height, enemies)
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
        step = config.AUTOPILOT_SPEED * dt
        if isinstance(self.autopilot_target, Planet):
            step = config.PLANET_LANDING_SPEED * dt
        if distance <= step:
            self.x = dest_x
            self.y = dest_y
            self.autopilot_target = None
            self.vx = 0
            self.vy = 0
            return
        self.angle = math.atan2(dy, dx)
        old_x, old_y = self.x, self.y
        self.x += dx / distance * step
        self.y += dy / distance * step
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
        for obj in self._enemy_list or []:
            other = getattr(obj, "ship", obj)
            if other is self:
                continue
            if math.hypot(other.x - self.x, other.y - self.y) < radius + other.collision_radius:
                return True
        for struct in self._structures:
            # Skip small drones so they don't trap the player when colliding.
            if isinstance(struct, Drone):
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

    def draw(self, screen: pygame.Surface, zoom: float = 1.0) -> None:
        """Draw the ship scaled by a non-linear factor of the zoom level."""
        cx = config.WINDOW_WIDTH // 2
        cy = config.WINDOW_HEIGHT // 2
        offset_x = self.x - cx / zoom
        offset_y = self.y - cy / zoom
        self.draw_particles(screen, offset_x, offset_y, zoom)
        points = self._triangle_points(cx, cy, zoom)
        pygame.draw.polygon(screen, self.color, points)

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
        if not self.weapons:
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
            if isinstance(weapon, MissileWeapon) and self._enemy_list:
                nearest = None
                min_d = float("inf")
                for en in self._enemy_list:
                    d = math.hypot(en.ship.x - self.x, en.ship.y - self.y)
                    if d < min_d:
                        min_d = d
                        nearest = en.ship
                if nearest:
                    weapon.target = nearest
                    proj = weapon.fire(self.x, self.y, nearest.x, nearest.y)
                else:
                    proj = weapon.fire(self.x, self.y, tx, ty)
            else:
                proj = weapon.fire(self.x, self.y, tx, ty)
        if proj:
            if isinstance(proj, (LaserBeam, TimedMine, Drone, BombDrone)):
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
            if isinstance(proj, (LaserBeam, TimedMine, Drone, BombDrone)):
                self.specials.append(proj)
            else:
                self.projectiles.append(proj)

    def use_artifact(self, index: int, enemies: list) -> None:
        """Activate an equipped artifact if possible."""
        if 0 <= index < len(self.artifacts):
            art = self.artifacts[index]
            if art.can_use():
                art.activate(self, enemies)

    def _update_projectiles(self, dt: float, world_width: int, world_height: int) -> None:
        for proj in list(self.projectiles):
            proj.update(dt)
            out_of_bounds = not (0 <= proj.x <= world_width and 0 <= proj.y <= world_height)
            if proj.expired() or out_of_bounds:
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

    def _update_specials(self, dt: float, world_width: int, world_height: int, enemies: list | None = None) -> None:
        for obj in list(self.specials):
            if isinstance(obj, LaserBeam):
                obj.update(dt, enemies or [])
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, TimedMine):
                obj.update(dt)
                if obj.exploded and enemies:
                    for en in enemies:
                        if math.hypot(en.ship.x - obj.x, en.ship.y - obj.y) <= obj.radius:
                            en.ship.take_damage(obj.damage)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, Drone):
                obj.update(dt, enemies or [])
                for proj in list(obj.projectiles):
                    for en in enemies or []:
                        if (
                            math.hypot(proj.x - en.ship.x, proj.y - en.ship.y)
                            <= en.ship.collision_radius
                        ):
                            en.ship.take_damage(proj.damage)
                            obj.projectiles.remove(proj)
                            break
                drone_rect = pygame.Rect(
                    obj.x - obj.size / 2,
                    obj.y - obj.size / 2,
                    obj.size,
                    obj.size,
                )
                for en in enemies or []:
                    for proj in list(en.ship.projectiles):
                        if drone_rect.collidepoint(proj.x, proj.y):
                            obj.hp -= proj.damage
                            en.ship.projectiles.remove(proj)
                            if obj.hp <= 0:
                                break
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, BombDrone):
                obj.update(dt, enemies or [])
                bomb_rect = pygame.Rect(
                    obj.x - obj.size / 2,
                    obj.y - obj.size / 2,
                    obj.size,
                    obj.size,
                )
                hit = False
                for en in enemies or []:
                    for proj in list(en.ship.projectiles):
                        if bomb_rect.collidepoint(proj.x, proj.y):
                            obj.hp -= proj.damage
                            en.ship.projectiles.remove(proj)
                            if obj.hp <= 0:
                                hit = True
                                break
                    if hit:
                        break
                    if (
                        math.hypot(en.ship.x - obj.x, en.ship.y - obj.y)
                        <= en.ship.collision_radius
                    ):
                        hit = True
                        break
                if hit:
                    obj._explode()
                if obj.exploded and enemies:
                    for en in enemies:
                        if math.hypot(en.ship.x - obj.x, en.ship.y - obj.y) <= obj.radius:
                            en.ship.take_damage(obj.damage)
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
                for en in enemies or []:
                    obj.apply_pull(en.ship, dt)
                if obj.expired():
                    self.specials.remove(obj)
            elif isinstance(obj, AreaShieldAura):
                # Intercept incoming projectiles while the aura holds
                for en in enemies or []:
                    for proj in list(en.ship.projectiles):
                        if math.hypot(proj.x - self.x, proj.y - self.y) <= obj.radius:
                            obj.take_damage(proj.damage)
                            en.ship.projectiles.remove(proj)
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
                obj.update(dt, enemies or [])
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
            obj.draw(screen, offset_x, offset_y, zoom)
        if self.area_shield:
            self.area_shield.draw(screen, offset_x, offset_y, zoom)

    def draw_particles(self, screen: pygame.Surface, offset_x: float = 0.0, offset_y: float = 0.0, zoom: float = 1.0) -> None:
        for p in self.particles:
            px = int((p.x - offset_x) * zoom)
            py = int((p.y - offset_y) * zoom)
            pygame.draw.circle(screen, p.color, (px, py), max(1, int(2 * zoom)))

    def draw_at(
        self,
        screen: pygame.Surface,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        zoom: float = 1.0,
    ) -> None:
        """Draw the ship on screen applying an offset and zoom."""
        if self.invisible_timer > 0:
            return
        self.draw_particles(screen, offset_x, offset_y, zoom)
        cx = int((self.x - offset_x) * zoom)
        cy = int((self.y - offset_y) * zoom)
        points = self._triangle_points(cx, cy, zoom)
        pygame.draw.polygon(screen, self.color, points)


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
