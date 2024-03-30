import pygame
import src.utils.classes


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    src.utils.classes.Game().game_intro()
