import pygame

class Scene:
    def __init__(self, screen, background=(0, 200, 200)):
        self.screen = screen
        self.bg = background
        self.objects = {}

    def add_object(self, game_object, layer: int):
        if layer not in self.objects:
            self.objects[layer] = []
        self.objects[layer].append(game_object)

    def draw(self, camera):
        self.screen.fill(self.bg)
        for layer in sorted(self.objects):
            for obj in self.objects[layer]:
                obj.draw(self.screen, camera)
        pygame.display.flip()
        self.objects.clear()
