import pygame
from core.game import Game
import settings


pygame.init()
screen = pygame.display.set_mode(settings.screensize)
pygame.display.set_caption("The Postman")
pygame.display.set_icon(pygame.image.load("assets\\icon.png"))
game = Game(screen)
game.run()
