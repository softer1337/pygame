import pygame
from scene import Scene
from objects.gameobjects import GameObject

class TextManager():
    def __init__(self, scene: Scene):
        self.scene = scene
        self.texts = []
        self.rects = []
        self.active_font = 0

    def add_text(self, text, size, pos, color=(0, 0, 0)):
        self.font1 = pygame.font.SysFont('arial', size)
        surface = self.font1.render(text, True, color)
        rect = surface.get_rect()
        rect.topleft = pos
        self.texts.append(surface)
        self.rects.append(rect)

    def draw(self):
        for i in range(len(self.texts)):
            pos = self.rects[i].topleft
            text_object = GameObject(surface=self.texts[i], pos=pos, scale=(self.texts[i].get_width(), self.texts[i].get_height()))
            self.scene.add_object(text_object, 100)
    
        self.texts = []
        self.rects = []
    def raw_draw(self):
        for i in range(len(self.texts)):
            pos = self.rects[i].topleft
            self.scene.screen.blit(self.texts[i], pos)
        self.texts.clear()
        self.rects.clear()
