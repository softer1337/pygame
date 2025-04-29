import pygame

class InputHandler:
    def __init__(self):
        self.keys_pressed = set()  
        self.mouse_buttons = set()  
        self.mouse_position = (0, 0)  

    def update(self):
        self.keys_pressed.clear()  
        self.mouse_buttons.clear()
        keys = pygame.key.get_pressed()
        for key in range(len(keys)):
            if keys[key]:
                self.keys_pressed.add(key)

        mouse_buttons = pygame.mouse.get_pressed()

        for i, pressed in enumerate(mouse_buttons):
            if pressed:
                self.mouse_buttons.add(i)

        self.mouse_position = pygame.mouse.get_pos()

    def is_key_pressed(self, key):
        return key in self.keys_pressed

    def is_mouse_button_pressed(self, button):
        return button in self.mouse_buttons

    def get_mouse_position(self):
        return self.mouse_position