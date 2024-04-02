import pygame
import src.utils.classes as classes


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    classes.Game().game_intro()
