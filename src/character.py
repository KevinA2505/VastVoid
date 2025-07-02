import pygame
import config
from fraction import FRACTIONS, Fraction
from items import ITEM_NAMES

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

class Player:
    """The player controlled character."""

    def __init__(self, name: str, age: int, species, fraction: Fraction, ship_model=None):
        self.name = name
        self.age = age
        self.species = species
        self.fraction = fraction
        self.ship_model = ship_model
        # Inventory starts empty but contains an entry for each known item
        self.inventory: dict[str, int] = {item: 0 for item in ITEM_NAMES}

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
