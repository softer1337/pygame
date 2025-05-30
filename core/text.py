import pygame
from scene import Scene
from objects.gameobjects import GameObject

class TextManager:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.texts = [] 
        self.font_cache = {}  
        self.created_objects = []  

    def get_font(self, size: int) -> pygame.font.Font:
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.SysFont('arial', size)
        return self.font_cache[size]

    def add_text(self, text: str, size: int, pos: tuple[int, int], color=(0, 0, 0)):
        font = self.get_font(size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(topleft=pos)
        self.texts.append((surface, rect))

    def draw(self):
        self.created_objects.clear()

        for surface, rect in self.texts:
            text_object = GameObject(
                surface=surface,
                pos=rect.topleft,
                scale=surface.get_size()
            )
            self.scene.add_object(text_object, layer=100)
            self.created_objects.append(text_object)

        self.texts.clear()

    def raw_draw(self):
        for surface, rect in self.texts:
            self.scene.screen.blit(surface, rect.topleft)
        self.texts.clear()
