import pygame
from dataclasses import dataclass
import config
from fraction import FRACTIONS, Fraction
from items import ITEMS_BY_NAME

class Alien:
    """Basic Alien species."""
    def __init__(self):
        self.species = "Alien"

class Human:
    """Basic Human species."""
    def __init__(self):
        self.species = "Human"

class Robot:
    """Basic Robot species."""
    def __init__(self):
        self.species = "Robot"


@dataclass
class CrewMember:
    """Simple crew member with a name and species."""

    name: str
    species: Human | Alien | Robot

class Player:
    """The player controlled character."""

    def __init__(
        self,
        name: str,
        age: int,
        species,
        fraction: Fraction,
        ship_model=None,
        credits: int = 0,
    ):
        self.name = name
        self.age = age
        self.species = species
        self.fraction = fraction
        self.ship_model = ship_model
        self.credits = credits
        # Inventory starts empty but contains an entry for each known item
        self.inventory: dict[str, int] = {name: 0 for name in ITEMS_BY_NAME}

    def add_item(self, item: str, quantity: int = 1) -> None:
        """Add `quantity` of `item` to the inventory."""
        if item not in self.inventory:
            self.inventory[item] = 0
        self.inventory[item] += quantity

    def remove_item(self, item: str, quantity: int = 1) -> None:
        """Remove up to `quantity` of `item` from the inventory."""
        if item not in self.inventory:
            return
        self.inventory[item] = max(0, self.inventory[item] - quantity)


def create_player(screen: pygame.Surface) -> Player:
    """Show a simple screen to create the player and return the Player object."""
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    name = ""
    age = ""
    step = 0  # 0-name,1-age,2-species,3-fraction
    species = None
    fraction = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if step == 0:
                    if event.key == pygame.K_RETURN:
                        if name:
                            step = 1
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode
                elif step == 1:
                    if event.key == pygame.K_RETURN:
                        if age:
                            step = 2
                    elif event.key == pygame.K_BACKSPACE:
                        age = age[:-1]
                    elif event.unicode.isdigit():
                        age += event.unicode
                elif step == 2:
                    key = event.unicode.lower()
                    if key == 'h':
                        species = Human()
                    elif key == 'a':
                        species = Alien()
                    elif key == 'r':
                        species = Robot()
                    if species:
                        step = 3
                elif step == 3:
                    if event.unicode.isdigit():
                        index = int(event.unicode) - 1
                        if 0 <= index < len(FRACTIONS):
                            fraction = FRACTIONS[index]
                            player = Player(name, int(age or 0), species, fraction)
                            # Give the player some starter supplies
                            player.add_item("gasolina", 10)
                            player.add_item("materia oscura", 1)
                            # The player starts with a partially burnt boat
                            player.add_item("boat", 1)
                            return player

        screen.fill(config.BACKGROUND_COLOR)
        if step == 0:
            msg1 = font.render("Enter name:", True, (255, 255, 255))
            msg2 = font.render(name + "|", True, (255, 255, 255))
            screen.blit(msg1, (50, 100))
            screen.blit(msg2, (50, 140))
        elif step == 1:
            msg1 = font.render("Enter age:", True, (255, 255, 255))
            msg2 = font.render(age + "|", True, (255, 255, 255))
            screen.blit(msg1, (50, 100))
            screen.blit(msg2, (50, 140))
        elif step == 2:
            lines = [
                "Choose species:",
                "H - Human", "A - Alien", "R - Robot"]
            for i, line in enumerate(lines):
                msg = font.render(line, True, (255, 255, 255))
                screen.blit(msg, (50, 100 + i * 30))
        else:
            lines = ["Choose fraction:"]
            lines += [f"{i+1} - {frac.name}" for i, frac in enumerate(FRACTIONS)]
            for i, line in enumerate(lines):
                msg = font.render(line, True, (255, 255, 255))
                screen.blit(msg, (50, 100 + i * 30))
        pygame.display.flip()
        clock.tick(30)


def choose_player(screen: pygame.Surface) -> Player:
    """Let the user pick an existing profile or create/delete one."""
    from savegame import list_players, load_player, delete_player, save_player

    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    deleting = False
    while True:
        profiles = list_players()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if deleting and event.unicode.isdigit():
                    idx = int(event.unicode) - 1
                    if 0 <= idx < len(profiles):
                        delete_player(profiles[idx])
                    deleting = False
                elif event.unicode.isdigit():
                    idx = int(event.unicode) - 1
                    if 0 <= idx < len(profiles):
                        return load_player(profiles[idx])
                elif event.unicode.lower() == "n":
                    player = create_player(screen)
                    save_player(player)
                    return player
                elif event.unicode.lower() == "d":
                    deleting = True

        screen.fill(config.BACKGROUND_COLOR)
        lines = ["Choose profile:"]
        for i, name in enumerate(profiles):
            lines.append(f"{i+1} - {name}")
        lines.append("N - New profile")
        lines.append("D - Delete profile")
        if deleting:
            lines.append("Select number to delete")
        for i, line in enumerate(lines):
            msg = font.render(line, True, (255, 255, 255))
            screen.blit(msg, (50, 100 + i * 30))
        pygame.display.flip()
        clock.tick(30)


def choose_player_table(screen: pygame.Surface) -> Player:
    """GUI with buttons to load or delete a profile."""
    from savegame import list_players, load_player, delete_player, save_player

    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    name_w, btn_w, row_h = 200, 100, 40
    spacing = 10
    start_x, start_y = 50, 100

    while True:
        profiles = list_players()
        row_rects: list[tuple[pygame.Rect, pygame.Rect]] = []
        y = start_y
        for _ in profiles:
            load_rect = pygame.Rect(start_x + name_w + spacing, y, btn_w, row_h)
            del_rect = pygame.Rect(
                start_x + name_w + spacing * 2 + btn_w, y, btn_w, row_h
            )
            row_rects.append((load_rect, del_rect))
            y += row_h + 5
        new_rect = pygame.Rect(start_x, y + 20, btn_w * 2, row_h)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, (load_rect, del_rect) in enumerate(row_rects):
                    if load_rect.collidepoint(event.pos):
                        return load_player(profiles[idx])
                    if del_rect.collidepoint(event.pos):
                        delete_player(profiles[idx])
                if new_rect.collidepoint(event.pos):
                    player = create_player(screen)
                    save_player(player)
                    return player

        screen.fill(config.BACKGROUND_COLOR)
        y = start_y
        for i, name in enumerate(profiles):
            name_rect = pygame.Rect(start_x, y, name_w, row_h)
            pygame.draw.rect(screen, (60, 60, 90), name_rect)
            pygame.draw.rect(screen, (200, 200, 200), name_rect, 1)
            txt = font.render(name, True, (255, 255, 255))
            screen.blit(txt, txt.get_rect(center=name_rect.center))

            load_rect, del_rect = row_rects[i]
            pygame.draw.rect(screen, (60, 60, 90), load_rect)
            pygame.draw.rect(screen, (200, 200, 200), load_rect, 1)
            load_txt = font.render("Load", True, (255, 255, 255))
            screen.blit(load_txt, load_txt.get_rect(center=load_rect.center))

            pygame.draw.rect(screen, (60, 60, 90), del_rect)
            pygame.draw.rect(screen, (200, 200, 200), del_rect, 1)
            del_txt = font.render("Delete", True, (255, 255, 255))
            screen.blit(del_txt, del_txt.get_rect(center=del_rect.center))
            y += row_h + 5

        pygame.draw.rect(screen, (60, 60, 90), new_rect)
        pygame.draw.rect(screen, (200, 200, 200), new_rect, 1)
        new_txt = font.render("New Profile", True, (255, 255, 255))
        screen.blit(new_txt, new_txt.get_rect(center=new_rect.center))

        pygame.display.flip()
        clock.tick(30)
