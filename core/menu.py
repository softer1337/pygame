import pygame
from objects.gameobjects import GameObject
from core.text import TextManager

class UIButton:
    def __init__(self, image_path, position, size, text, font_size, text_color, on_click=None):
        self.game_object = GameObject(image_path, position, size)
        self.rect = pygame.Rect(position, size)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.on_click = on_click

    def update(self, input_handler):
        if input_handler.is_mouse_button_pressed(0):
            if self.rect.collidepoint(input_handler.get_mouse_position()):
                if self.on_click:
                    self.on_click()

    def draw(self, scene, text_manager):
        scene.add_object(self.game_object, 1)

        font = pygame.font.SysFont(None, self.font_size)
        text_surface = font.render(self.text, True, self.text_color)
        text_x = self.rect.centerx - text_surface.get_width() // 2
        text_y = self.rect.centery - text_surface.get_height() // 2
        text_manager.add_text(self.text, self.font_size, (text_x, text_y), self.text_color)



class MenuScene:
    def __init__(self, scene, input_handler, on_start_callback, text_manager: TextManager, camera):
        self.scene = scene
        self.input = input_handler
        self.text_manager = text_manager
        self.camera = camera

        # Фон
        self.bg = GameObject('assets\\bg.png', (0, 0), (1280, 720))

        # Кнопка "Start"
        self.start_button = UIButton(
            image_path='assets\\wall.jpg',
            position=(540, 360),  # центр экрана
            size=(200, 80),
            text="Start",
            font_size=36,
            text_color=(255, 255, 255),
            on_click=on_start_callback
        )

    def update(self):
        self.start_button.update(self.input)

    def draw(self):
        self.scene.add_object(self.bg, 0)

        # Заголовок
        self.text_manager.add_text("The Postman", 60, (1280//2 - 150, 200), (255, 255, 255))

        # Кнопка
        self.start_button.draw(self.scene, self.text_manager)
