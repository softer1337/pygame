import pygame
from core.game import Game
import settings


pygame.init()
screen = pygame.display.set_mode(settings.screensize)
pygame.display.set_caption("bruh")
game = Game(screen)
game.run()
