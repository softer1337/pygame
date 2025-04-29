import pygame
from objects.gameobjects import GameObject

class MenuScene:
    def __init__(self, scene, input_handler, on_start_callback):
        self.scene = scene
        self.input = input_handler
        self.on_start = on_start_callback

        self.bg = GameObject('assets\\bg.jpg', (0, 0), (1280, 720))
        self.title = GameObject('assets\\players.png', (400, 100), (500, 100))
        self.start_button = GameObject('assets\\playerm1.png', (540, 300), (200, 80))

    def update(self):
        mouse_pos = self.input.get_mouse_position()
        if self.input.is_mouse_button_pressed(0):
            if self.start_button.get_rect().collidepoint(mouse_pos):
                self.on_start()

    def draw(self):
        self.scene.add_object(self.bg, 0)
        self.scene.add_object(self.title, 1)
        self.scene.add_object(self.start_button, 2)
