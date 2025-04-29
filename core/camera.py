import pygame

class Camera:
    def __init__(self):
        self.pos = pygame.Vector2(0, 0) 
    def apply(self, pos):
        return (int(pos[0] - self.pos[0]), int(pos[1] - self.pos[1]))


    def set_position(self, x, y):

        self.pos.x = x
        self.pos.y = y

    def move(self, dx, dy):

        self.pos.x += dx
        self.pos.y += dy
