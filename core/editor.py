import pygame
import json
from scene import Scene
from object_manager import ObjectManager
from trigger import TriggerManager
from camera import Camera
from utils.input import InputHandler

class Editor:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 600
        self.panel_width = 200
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Редактор карт")
        self.clock = pygame.time.Clock()
        self.running = True

        # Сцена и менеджеры (заглушки, можно расширить интеграцию)
        self.scene = Scene(self.screen)
        self.object_manager = ObjectManager()
        self.trigger_manager = TriggerManager()
        self.camera = Camera()
        self.input = InputHandler()

        # Состояние редактора
        self.selected_type = None  # "Wall", "SpawnPoint", "Collider"
        self.trigger_name = ""
        self.selected_object = None
        self.dragging = False
        self.resizing = False
        self.confirm_save = False
        self.input_active = False  # Фокус ввода имени триггера
        self.message = ""
        self.message_timer = 0

        # Элементы интерфейса: кнопки и поле ввода
        self.font = pygame.font.SysFont(None, 24)
        self.large_font = pygame.font.SysFont(None, 32)
        y = 20
        self.type_buttons = {}
        for obj_type in ["wall", "spawnpoint", "collider"]:
            rect = pygame.Rect(10, y, self.panel_width-20, 30)
            self.type_buttons[obj_type] = rect
            y += 40
        self.input_rect = pygame.Rect(10, y, self.panel_width-20, 30)
        y += 50
        self.save_button = pygame.Rect(10, y, self.panel_width-20, 30)
        self.load_button = pygame.Rect(10, y+40, self.panel_width-20, 30)
        self.confirm_rect = pygame.Rect(self.width//2-150, self.height//2-60, 300, 120)
        self.confirm_yes = pygame.Rect(self.confirm_rect.x+30, self.confirm_rect.y+60, 100, 30)
        self.confirm_no = pygame.Rect(self.confirm_rect.x+170, self.confirm_rect.y+60, 100, 30)

        # Список объектов карты
        self.objects = []

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.confirm_save:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.confirm_yes.collidepoint(event.pos):
                        self.do_save()
                        self.confirm_save = False
                    elif self.confirm_no.collidepoint(event.pos):
                        self.confirm_save = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.on_left_down(event)
                elif event.button == 3:
                    self.on_right_down(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.on_left_up(event)
            elif event.type == pygame.MOUSEMOTION:
                self.on_mouse_motion(event)
            elif event.type == pygame.KEYDOWN:
                self.on_key_down(event)

    def on_left_down(self, event):
        x, y = event.pos
        # Клик по области панели
        if x < self.panel_width:
            self.input_active = False
            # Кнопки выбора типа
            for obj_type, rect in self.type_buttons.items():
                if rect.collidepoint(event.pos):
                    # Переключаем выбор типа объекта
                    self.selected_type = None if self.selected_type == obj_type else obj_type
                    return
            # Поле ввода имени триггера
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
                return
            # Сохранить/Загрузить
            if self.save_button.collidepoint(event.pos):
                self.confirm_save = True
                return
            if self.load_button.collidepoint(event.pos):
                self.load_map()
                return
            return

        # Клик по области карты
        self.input_active = False
        world_x = x - self.panel_width - self.camera.pos.x
        world_y = y - self.camera.pos.y

        # Добавление нового объекта, если выбран тип
        if self.selected_type:
            grid = 40
            wx = int(world_x // grid) * grid
            wy = int(world_y // grid) * grid
            new_rect = pygame.Rect(wx, wy, 40, 40)
            obj = {"type": self.selected_type, "rect": new_rect, "trigger": ""}
            if self.trigger_name.strip():
                self.trigger_manager.add_trigger(self.trigger_name.strip())
                obj["trigger"] = self.trigger_name.strip()
            self.objects.append(obj)
            self.trigger_name = ""
            return

        # Выбор существующего объекта
        for obj in reversed(self.objects):
            screen_rect = obj["rect"].move(self.camera.pos.x + self.panel_width, self.camera.pos.y)
            if screen_rect.collidepoint(event.pos):
                self.selected_object = obj
                self.dragging = True
                mx, my = world_x, world_y
                self.drag_offset = (mx - obj["rect"].x, my - obj["rect"].y)
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    self.resizing = True
                    self.resize_start = (mx, my)
                    self.resize_orig = (obj["rect"].width, obj["rect"].height)
                else:
                    self.resizing = False
                return
        self.selected_object = None

    def on_right_down(self, event):
        x, y = event.pos
        if x < self.panel_width:
            return
        for obj in reversed(self.objects):
            screen_rect = obj["rect"].move(self.camera.pos.x + self.panel_width, self.camera.pos.y)
            if screen_rect.collidepoint(event.pos):
                self.objects.remove(obj)
                if self.selected_object == obj:
                    self.selected_object = None
                break

    def on_left_up(self, event):
        self.dragging = False
        self.resizing = False

    def on_mouse_motion(self, event):
        x, y = event.pos
        if x < self.panel_width or not self.selected_object or not self.dragging:
            return
        world_x = x - self.panel_width - self.camera.pos.x
        world_y = y - self.camera.pos.y
        if self.resizing:
            dx = world_x - self.resize_start[0]
            dy = world_y - self.resize_start[1]
            new_w = max(20, self.resize_orig[0] + dx)
            new_h = max(20, self.resize_orig[1] + dy)
            self.selected_object["rect"].width = new_w
            self.selected_object["rect"].height = new_h
        else:
            new_x = world_x - self.drag_offset[0]
            new_y = world_y - self.drag_offset[1]
            self.selected_object["rect"].x = new_x
            self.selected_object["rect"].y = new_y


    def on_key_down(self, event):
        if self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.trigger_name = self.trigger_name[:-1]
            elif event.key == pygame.K_RETURN:
                self.input_active = False
            else:
                char = event.unicode
                if char.isalnum() or char == '_':
                    self.trigger_name += char
            return

        # Перемещение камеры
        if event.key == pygame.K_w:
            self.camera.pos.y += 10
        elif event.key == pygame.K_s:
            self.camera.pos.y -= 10
        elif event.key == pygame.K_a:
            self.camera.pos.x += 10
        elif event.key == pygame.K_d:
            self.camera.pos.x -= 10

    def load_map(self):
        try:
            with open("map.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            self.objects.clear()
            for entry in data:
                obj_type = entry.get("type")
                if obj_type == "bg":
                    rect = pygame.Rect(0, 0, 0, 0)  # Просто заглушка
                    trigger = ""
                else:
                    pos = entry.get("pos", {"x": 0, "y": 0})
                    size = entry.get("size", {"width": 40, "height": 40})
                    trigger = entry.get("trigger", {}).get("name", "")
                    rect = pygame.Rect(pos["x"], pos["y"], size["width"], size["height"])
                    if trigger:
                        self.trigger_manager.add(trigger)
                obj = {"type": obj_type, "rect": rect, "trigger": trigger}
                self.objects.append(obj)
        except Exception as e:
            print("Ошибка загрузки:", e)



    def do_save(self):
        data = []
        for obj in self.objects:
            entry = {
                "type": obj["type"]
            }
            
            if obj["type"] == "bg":
                entry["texture"] = "assets\\bg.jpg"
            
            else:
                # Для wall, collider, spawnpoint
                entry["pos"] = {
                    "x": obj["rect"].x,
                    "y": obj["rect"].y
                }
                
                if obj["type"] in ("wall", "collider"):
                    entry["size"] = {
                        "width": obj["rect"].width,
                        "height": obj["rect"].height
                    }
                    entry["layer"] = 2
                
                if obj["type"] == "wall":
                    entry["texture"] = "assets\\wall.jpg"
                    entry["collidable"] = True
                
                if obj["trigger"]:
                    entry["trigger"] = {"name": obj["trigger"]}
            
            data.append(entry)
        
        try:
            with open("map.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            self.message = "Карта сохранена"
            self.message_timer = 180
        except Exception as e:
            print("Ошибка сохранения:", e)



    def update(self):
        if self.message_timer > 0:
            self.message_timer -= 1
        else:
            self.message = ""

    def draw(self):
        # Фон панели
        self.screen.fill((50, 50, 50), (0, 0, self.panel_width, self.height))
        # Заголовок
        title = self.large_font.render("Редактор карт", True, (255,255,255))
        self.screen.blit(title, (10, 5))
        # Кнопки типов объектов
        for obj_type, rect in self.type_buttons.items():
            color = (100,100,100) if self.selected_type == obj_type else (80,80,80)
            pygame.draw.rect(self.screen, color, rect)
            txt = self.font.render(obj_type, True, (255,255,255))
            self.screen.blit(txt, (rect.x+5, rect.y+5))
        # Поле ввода имени триггера
        pygame.draw.rect(self.screen, (100,100,100), self.input_rect)
        label = self.font.render("Имя триггера:", True, (255,255,255))
        self.screen.blit(label, (self.input_rect.x, self.input_rect.y - 20))
        txt = self.font.render(self.trigger_name, True, (255,255,0))
        self.screen.blit(txt, (self.input_rect.x+5, self.input_rect.y+5))
        # Кнопки сохранения/загрузки
        pygame.draw.rect(self.screen, (80,80,80), self.save_button)
        pygame.draw.rect(self.screen, (80,80,80), self.load_button)
        save_lbl = self.font.render("Сохранить карту", True, (255,255,255))
        load_lbl = self.font.render("Загрузить карту", True, (255,255,255))
        self.screen.blit(save_lbl, (self.save_button.x+5, self.save_button.y+5))
        self.screen.blit(load_lbl, (self.load_button.x+5, self.load_button.y+5))
        # Текущий выбранный тип
        cur = self.selected_type if self.selected_type else "None"
        cur_lbl = self.font.render(f"Выбрано: {cur}", True, (255,255,255))
        self.screen.blit(cur_lbl, (10, self.save_button.y+40))

        # Область карты и сетка
        self.screen.fill((150,150,150), (self.panel_width, 0, self.width-self.panel_width, self.height))
        grid = 40
        for gx in range(0, self.width-self.panel_width, grid):
            pygame.draw.line(self.screen, (200,200,200), (self.panel_width+gx, 0), (self.panel_width+gx, self.height))
        for gy in range(0, self.height, grid):
            pygame.draw.line(self.screen, (200,200,200), (self.panel_width, gy), (self.width, gy))

        # Отрисовка объектов
        for obj in self.objects:
            col = (100,100,100) if obj["type"]=="wall" else (50,200,50) if obj["type"]=="spawnpoint" else (200,50,50)
            rect = obj["rect"].copy()
            rect.x += self.camera.pos.x + self.panel_width
            rect.y += self.camera.pos.y
            pygame.draw.rect(self.screen, col, rect)
            if obj["trigger"]:
                txt = self.font.render(obj["trigger"], True, (255,255,0))
                self.screen.blit(txt, (rect.x+5, rect.y+5))
            if obj == self.selected_object:
                pygame.draw.rect(self.screen, (255,255,0), rect, 2)

        # Диалог подтверждения сохранения
        if self.confirm_save:
            pygame.draw.rect(self.screen, (60,60,60), self.confirm_rect)
            q = self.font.render("Сохранить карту?", True, (255,255,255))
            self.screen.blit(q, (self.confirm_rect.x+30, self.confirm_rect.y+20))
            pygame.draw.rect(self.screen, (80,80,80), self.confirm_yes)
            pygame.draw.rect(self.screen, (80,80,80), self.confirm_no)
            yes = self.font.render("Да", True, (255,255,255))
            no  = self.font.render("Нет", True, (255,255,255))
            self.screen.blit(yes, (self.confirm_yes.x+30, self.confirm_yes.y+5))
            self.screen.blit(no, (self.confirm_no.x+30, self.confirm_no.y+5))

        # Сообщение (например, «Карта сохранена»)
        if self.message:
            msg = self.font.render(self.message, True, (255,255,0))
            self.screen.blit(msg, (self.panel_width+10, 10))

        pygame.display.flip()

if __name__ == "__main__":
    editor = Editor()
    editor.run()
