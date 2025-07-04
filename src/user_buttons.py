import pygame
import config
from character import choose_player_table



def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption("User Manager")
    font = pygame.font.Font(None, 32)
    clock = pygame.time.Clock()

    btn_w, btn_h = 200, 40
    start_y = config.WINDOW_HEIGHT // 2 - btn_h - 10
    load_rect = pygame.Rect((config.WINDOW_WIDTH - btn_w) // 2, start_y, btn_w, btn_h)
    delete_rect = pygame.Rect((config.WINDOW_WIDTH - btn_w) // 2, start_y + btn_h + 20, btn_w, btn_h)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if load_rect.collidepoint(event.pos):
                    choose_player_table(screen)
                elif delete_rect.collidepoint(event.pos):
                    choose_player_table(screen)
        screen.fill(config.BACKGROUND_COLOR)
        pygame.draw.rect(screen, (60, 60, 90), load_rect)
        pygame.draw.rect(screen, (200, 200, 200), load_rect, 1)
        load_txt = font.render("Load User", True, (255, 255, 255))
        screen.blit(load_txt, load_txt.get_rect(center=load_rect.center))

        pygame.draw.rect(screen, (60, 60, 90), delete_rect)
        pygame.draw.rect(screen, (200, 200, 200), delete_rect, 1)
        del_txt = font.render("Delete User", True, (255, 255, 255))
        screen.blit(del_txt, del_txt.get_rect(center=delete_rect.center))

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
