import pygame
import config
from tech_tree import TECH_TREE, ResearchManager


def _compute_levels() -> dict[int, list[str]]:
    """Return a mapping of depth levels to tech IDs.

    Raises
    ------
    KeyError
        If a prerequisite references a non-existent technology ID.
    ValueError
        If the prerequisites form a cycle.
    """

    cache: dict[str, int] = {}
    visiting: set[str] = set()

    def depth(tid: str) -> int:
        if tid in cache:
            return cache[tid]
        if tid in visiting:
            raise ValueError(f"Cyclic prerequisite detected at '{tid}'")
        node = TECH_TREE.get(tid)
        if node is None:
            raise KeyError(f"Unknown technology id '{tid}'")
        visiting.add(tid)
        if not node.prerequisites:
            cache[tid] = 0
            visiting.remove(tid)
            return 0
        prereq_depths: list[int] = []
        for p in node.prerequisites:
            if p not in TECH_TREE:
                raise KeyError(f"Prerequisite '{p}' for '{tid}' does not exist")
            prereq_depths.append(depth(p))
        d = 1 + max(prereq_depths)
        cache[tid] = d
        visiting.remove(tid)
        return d

    levels: dict[int, list[str]] = {}
    for tid in TECH_TREE:
        lvl = depth(tid)
        levels.setdefault(lvl, []).append(tid)
    return levels


def _layout_nodes(levels: dict[int, list[str]], width: int) -> dict[str, pygame.Rect]:
    """Return pygame rects for each tech id based on their level."""
    rects: dict[str, pygame.Rect] = {}
    node_w, node_h = 160, 40
    margin_x, level_h = 40, 120
    for lvl, nodes in sorted(levels.items()):
        total_w = len(nodes) * (node_w + margin_x) - margin_x
        start_x = (width - total_w) // 2
        y = 60 + lvl * level_h
        for i, tid in enumerate(nodes):
            x = start_x + i * (node_w + margin_x)
            rects[tid] = pygame.Rect(x, y, node_w, node_h)
    return rects


def draw_tree(screen: pygame.Surface, font: pygame.font.Font, rects: dict[str, pygame.Rect], mgr: ResearchManager) -> None:
    """Draw technology nodes and the lines linking prerequisites."""
    screen.fill((20, 20, 40))
    for tid, node in TECH_TREE.items():
        for pre in node.prerequisites:
            pygame.draw.line(screen, (200, 200, 200), rects[pre].midbottom, rects[tid].midtop, 2)
    for tid, rect in rects.items():
        color = (80, 80, 80)
        if tid in mgr.completed:
            color = (0, 120, 0)
        elif tid in mgr.in_progress:
            color = (40, 40, 160)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        txt = font.render(TECH_TREE[tid].name, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=rect.center))


def draw_info(screen: pygame.Surface, font: pygame.font.Font, tid: str | None, mgr: ResearchManager) -> pygame.Rect | None:
    """Render info panel for selected node and return start button rect."""
    if not tid:
        return None
    node = TECH_TREE[tid]
    x, y = 20, 360
    lines = [node.name, f"Cost: {node.cost}", node.description]
    if tid in mgr.in_progress:
        lines.append(f"Progress: {mgr.in_progress[tid]:.0f}/{node.cost}")
    if tid in mgr.completed:
        lines.append("Completed")
    for i, line in enumerate(lines):
        txt = font.render(line, True, (255, 255, 255))
        screen.blit(txt, (x, y + i * 24))
    if mgr.can_start(tid):
        rect = pygame.Rect(x, y + len(lines) * 24 + 10, 140, 30)
        pygame.draw.rect(screen, (60, 120, 60), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        stxt = font.render("Start", True, (255, 255, 255))
        screen.blit(stxt, stxt.get_rect(center=rect.center))
        return rect
    return None


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tech Tree")
    font = pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    mgr = ResearchManager()
    levels = _compute_levels()
    rects = _layout_nodes(levels, 800)
    selected: str | None = None
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        start_rect = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected and start_rect and start_rect.collidepoint(event.pos):
                    mgr.start(selected)
                else:
                    selected = None
                    for tid, rect in rects.items():
                        if rect.collidepoint(event.pos):
                            selected = tid
                            break
        mgr.advance(dt * 20)
        draw_tree(screen, font, rects, mgr)
        start_rect = draw_info(screen, font, selected, mgr)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
