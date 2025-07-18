import math
import random
import pygame
from star import Star
from planet import Planet
from station import SpaceStation
from names import get_system_name
from asteroid import Asteroid

class StarSystem:
    """Collection of a star with orbiting planets."""

    _id_counter = 1

    def __init__(self, x: int, y: int) -> None:
        self.name = get_system_name()
        StarSystem._id_counter += 1
        self.star = Star.random_star(x, y)
        self.planets = []
        num_planets = random.randint(2, 5)

        # Starting distance ensures planets don't overlap the star
        distance = self.star.radius + 40
        for _ in range(num_planets):
            self.planets.append(
                Planet.random_planet(self.star, distance)
            )

            # Increment distance so orbits are spaced apart
            distance += random.randint(30, 50)

        self.stations = []
        num_stations = 1  # fewer stations generated
        station_distance = distance
        for _ in range(num_stations):
            self.stations.append(
                SpaceStation.random_station(self.star, station_distance)
            )
            station_distance += random.randint(30, 50)

        # Generate a simple asteroid belt between the star and the outer planets
        self.asteroids: list[Asteroid] = []
        belt_inner = self.star.radius + 20
        belt_outer = distance - 20
        num_asteroids = random.randint(5, 15)
        for _ in range(num_asteroids):
            self.asteroids.append(
                Asteroid.random_near_star(self.star, belt_inner, belt_outer)
            )

    def update(self, dt: float = 0.0) -> None:
        for planet in self.planets:
            planet.update()
        for station in self.stations:
            station.update(dt)
        # Remove any depleted asteroids
        self.asteroids = [a for a in self.asteroids if not a.depleted()]

    def collides_with_point(self, x: float, y: float, radius: float) -> bool:
        if math.hypot(self.star.x - x, self.star.y - y) < self.star.radius + radius:
            return True
        for planet in self.planets:
            if math.hypot(planet.x - x, planet.y - y) < planet.radius + radius:
                return True
        for asteroid in self.asteroids:
            if math.hypot(asteroid.x - x, asteroid.y - y) < asteroid.radius + radius:
                return True
        for station in self.stations:
            if station.collides_with_point(x, y, radius):
                return True
        return False

    def get_object_at_point(self, x: float, y: float, radius: float):
        """Return the star, planet or station under the point if any."""
        if math.hypot(self.star.x - x, self.star.y - y) < self.star.radius + radius:
            return self.star
        for planet in self.planets:
            if math.hypot(planet.x - x, planet.y - y) < planet.radius + radius:
                return planet
        for asteroid in self.asteroids:
            if math.hypot(asteroid.x - x, asteroid.y - y) < asteroid.radius + radius:
                return asteroid
        for station in self.stations:
            if math.hypot(station.x - x, station.y - y) < station.radius + radius:
                return station
        return None

    def draw(
        self,
        screen: pygame.Surface,
        offset_x: float = 0,
        offset_y: float = 0,
        zoom: float = 1.0,
    ) -> None:
        self.star.draw(screen, offset_x, offset_y, zoom)
        for planet in self.planets:
            # Draw orbit path for visualization
            pygame.draw.circle(
                screen,
                (80, 80, 120),
                (
                    int((self.star.x - offset_x) * zoom),
                    int((self.star.y - offset_y) * zoom),
                ),
                int(planet.distance * zoom),
                1,
            )
            planet.draw(screen, offset_x, offset_y, zoom)

        for station in self.stations:
            station.draw(screen, offset_x, offset_y, zoom)

        for asteroid in self.asteroids:
            asteroid.draw(screen, offset_x, offset_y, zoom)
