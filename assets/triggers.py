from core.trigger import *
import pygame

c = 0

def p():
    global c
    c += 1
    print(c)

triggers = {
    "wallc1": ZoneTrigger((700, 600, 64, 64), pygame.Rect(0, 0, 0, 0), p, False)
}
