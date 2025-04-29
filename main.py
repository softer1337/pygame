import pygame
from core.game import Game
from core.editor import Editor
import settings


if settings.mode == "release":
    pygame.init()
    screen = pygame.display.set_mode(settings.screensize)
    pygame.display.set_caption("bruh")
    game = Game(screen)
    game.run()
elif settings.mode == "editor":
    editor = Editor()
    editor.run()
