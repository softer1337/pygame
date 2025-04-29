import pygame

class Scene():
    def __init__(self,screen):
        self.screen = screen
        self.objects = {}
        self.bg = (0,200,200)
    def add_object(self, game_object, layer: int):
        if layer not in self.objects:
            self.objects[layer] = []
        self.objects[layer].append(game_object)

    def draw(self, camera):
        self.screen.fill(self.bg)
        for layer in sorted(self.objects.keys()):
            for obj in self.objects[layer]:
                obj.draw(self.screen, camera)

        pygame.display.flip()
        self.objects = {}

