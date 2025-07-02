import pygame
import config

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
    def __init__(self, name: str, age: int, species):
        self.name = name
        self.age = age
        self.species = species


def create_player(screen: pygame.Surface) -> Player:
    """Show a simple screen to create the player and return the Player object."""
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()
    name = ""
    age = ""
    step = 0  # 0-name,1-age,2-species
    species = None

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
                        return Player(name, int(age or 0), species)

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
        else:
            lines = [
                "Choose species:",
                "H - Human", "A - Alien", "R - Robot"]
            for i, line in enumerate(lines):
                msg = font.render(line, True, (255, 255, 255))
                screen.blit(msg, (50, 100 + i * 30))
        pygame.display.flip()
        clock.tick(30)
