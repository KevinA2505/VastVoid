import heapq
import math
from typing import List, Tuple


Point = Tuple[float, float]


def _gather_obstacles(sectors: list, blackholes: list | None, margin: float = 40.0) -> list[tuple[float, float, float]]:
    """Collect planet and black hole positions with radii."""
    obstacles: list[tuple[float, float, float]] = []
    for sector in sectors:
        for system in getattr(sector, "systems", []):
            for planet in getattr(system, "planets", []):
                obstacles.append((planet.x, planet.y, planet.radius + margin))
        for hole in getattr(sector, "blackholes", []):
            obstacles.append((hole.x, hole.y, hole.radius + margin))
    if blackholes:
        for hole in blackholes:
            obstacles.append((hole.x, hole.y, hole.radius + margin))
    return obstacles


def find_safe_path(
    start: Point,
    goal: Point,
    sectors: list,
    blackholes: list | None,
    world_width: int,
    world_height: int,
    cell_size: int = 100,
    margin: float = 40.0,
) -> List[Point]:
    """Return a list of waypoints from start to goal avoiding obstacles."""
    obstacles = _gather_obstacles(sectors, blackholes, margin)

    cols = world_width // cell_size + 1
    rows = world_height // cell_size + 1

    def to_cell(p: Point) -> tuple[int, int]:
        return int(p[0] // cell_size), int(p[1] // cell_size)

    def center(cell: tuple[int, int]) -> Point:
        return (
            cell[0] * cell_size + cell_size / 2,
            cell[1] * cell_size + cell_size / 2,
        )

    start_cell = to_cell(start)
    goal_cell = to_cell(goal)

    def in_bounds(c: tuple[int, int]) -> bool:
        return 0 <= c[0] < cols and 0 <= c[1] < rows

    def is_blocked(c: tuple[int, int]) -> bool:
        if c == start_cell or c == goal_cell:
            return False
        cx, cy = center(c)
        for ox, oy, r in obstacles:
            if math.hypot(ox - cx, oy - cy) <= r:
                return True
        return False

    def heuristic(a: tuple[int, int], b: tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(open_set, (0.0, start_cell))
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score = {start_cell: 0.0}
    f_score = {start_cell: heuristic(start_cell, goal_cell)}
    closed: set[tuple[int, int]] = set()

    neighbors = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ]

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal_cell:
            path = [center(current)]
            while current in came_from:
                current = came_from[current]
                path.append(center(current))
            path.reverse()
            return path
        closed.add(current)
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if not in_bounds(neighbor) or neighbor in closed:
                continue
            if is_blocked(neighbor):
                continue
            tentative_g = g_score[current] + math.hypot(dx, dy)
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal_cell)
                f_score[neighbor] = f
                heapq.heappush(open_set, (f, neighbor))

    # Fallback: direct path if no route found
    return [goal]
