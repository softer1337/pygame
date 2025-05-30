import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pygame,random,time
from utils.input import InputHandler
from scene import Scene
from object_manager import ObjectManager
from objects.gameobjects import GameObject,Inventory,Item
from camera import Camera
from trigger import TriggerManager, ZoneTrigger, KeyTrigger, TimerTrigger
from menu import MenuScene
import utils.map_loader as map_loader
from settings import *
from text import TextManager

items = [
    Item("Еда", 100, 2),
    Item("Вода", 30, 4),
    Item("Аптечка", 200, 1),
    Item("Одежда", 150, 3),
    Item("Инструменты", 300, 4),
    Item("Радио", 400, 2),
    Item("Карта", 50, 1),
    Item("Фонарь", 180, 2),
    Item("Палатка", 350, 7),
    Item("Спички", 20, 1),
    Item("Канистра", 280, 5),
    Item("Зарядное устройство", 220, 2),
    Item("Сигнальные ракеты", 150, 3),
    Item("Защитная маска", 300, 2),
    Item("Рюкзак", 500, 6),
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.input = InputHandler()
        self.camera = Camera()
        self.state = "menu"
        self.is_moving = False
        self.last_move = 'd'
        self.deltaTime = self.clock.tick(60) / 1000.0

        self.player_speed = 150
        self.hotkeypressed = False
        self.debug_mode = False
        self.vertical_speed = 0
        self.is_on_ground = False
        self.gravity = gravity 
        self.jump_power = jump_power
        self.sprint_power = sprint_power
        self.sprint = False
        self.score = 0
        

        self.scene = Scene(screen)
        self.switch_to_menu()

    def switch_to_menu(self):
        self.state = "menu"
        self.camera = Camera()
        self.scene = Scene(self.screen)
        self.text_manager = TextManager(self.scene)
        self.menu_scene = MenuScene(self.scene, self.input, self.switch_to_gameplay,self.text_manager,self.camera)
        

    def jump(self):
        if self.is_on_ground:
            self.vertical_speed = self.jump_power
            self.is_on_ground = False
            self.m_heal(0.1)


    def swich_fps(self):
        if not self.hotkeypressed:
            self.debug_mode = not self.debug_mode
            self.hotkeypressed = True
 



    def switch_to_gameplay(self):
        self.state = "gameplay"
        self.scene = Scene(self.screen)
        self.text_manager = TextManager(self.scene)
        self.objectmanager = ObjectManager()
        self.triggermanager = TriggerManager()
        self.inventory = Inventory()


        self.player = GameObject('assets\\player\\frame_0.png', (100, 450),spawnable=True,collidable=True,tag='player')
        self.player.add_texture('assets\\player\\frame_1.png')
        self.player.add_texture('assets\\player\\frame_2.png')
        self.player.add_texture('assets\\player\\frame_3.png')
        self.player.add_texture('assets\\player\\frame_4.png')
        self.player.add_texture('assets\\player\\frame_5.png')
        self.player.add_texture('assets\\player\\frame_6.png')
        self.player.add_texture('assets\\player\\frame_7.png')
        self.player.add_texture('assets\\player\\frame_8.png')
        self.player.add_texture('assets\\player\\frame_9.png')
        self.objectmanager.add_object(self.player, 2)

        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_a, lambda: self.move(-1), self.input, once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_d, lambda: self.move(1), self.input, once=False)
        )
        self.triggermanager.add_trigger(
            TimerTrigger(150, self.anim, once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_q,self.swich_fps,self.input,once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_SPACE, self.jump, self.input, once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_ESCAPE, self.switch_to_menu, self.input, once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_LSHIFT, self.switch_speed,input_handler=self.input,once=False)
        )
        map_loader.load_scene_from_json(
            self.objectmanager,
            self.triggermanager,
            "assets/levels/level1/level1.json",
            self.player
        )

        for trig in list(self.triggermanager.triggers):
            if isinstance(trig, ZoneTrigger):
                trig.get_target_rect = self.player.get_rect
                if mode == "debug":print(f"[DEBUG] Bound ZoneTrigger at {trig.rect} to player.rect")

    def move(self, direction):
        
        if self.sprint == True:
            dx = direction * self.player_speed * self.deltaTime * self.sprint_power
        else:
            dx = direction * self.player_speed * self.deltaTime
        self.player.move_with_collisions(dx, 0, self.objectmanager.get_collidables())
        if direction != 0:
            if (direction > 0 and self.last_move != 'd') or (direction < 0 and self.last_move != 'a'):
                self.player.flip()
                self.last_move = 'd' if direction > 0 else 'a'
        self.is_moving = direction != 0
        self.sprint = False
        print(dx)
    def anim(self):
        if self.is_moving:
            self.player.swap_texture()
        else:
            self.player.active_texture = 0

        for trigger in self.triggermanager.triggers:
            if isinstance(trigger, TimerTrigger) and not trigger.once:
                trigger.reset()

    def get_and_write_score(self):
        with open("max_score.txt", 'r', encoding='utf-8') as file:
            old_score = float(file.read())

        if old_score < self.score:
            with open("max_score.txt", 'w', encoding='utf-8') as file:
                file.write(str(self.score))

        return old_score


    def draw_overlay(self):
        if self.debug_mode:
            fps = self.clock.get_fps()
            self.text_manager.add_text("FPS: "+str(round(fps,2)),     15, self.camera.pos+(5,  0), (255,255,255))
            self.text_manager.add_text("Triggers count: "+str(len(self.triggermanager.triggers)), 
                                                                    15, self.camera.pos+(5, 15), (255,255,255))
            self.text_manager.add_text("Activated triggers count: "+str(len(self.triggermanager.activated)), 
                                                                    15, self.camera.pos+(5, 30), (255,255,255))
                    
            self.text_manager.add_text("Objects count: "+str(len(self.objectmanager.objects)),  
                                                                    15, self.camera.pos+(5, 45), (255,255,255))
            self.text_manager.add_text("Input/KeyPressed: "+str(self.input.keys_pressed),      
                                                                    15, self.camera.pos+(5, 60), (255,255,255))
            self.text_manager.add_text("Input/MousePressed: "+str(self.input.mouse_buttons),
                                                                    15, self.camera.pos+(5, 75), (255,255,255))
            self.text_manager.add_text("Input/MousePos: "+str(self.input.mouse_position),
                                                                    15, self.camera.pos+(5, 90), (255,255,255))
            self.text_manager.add_text("Player pos: "+str(self.objectmanager.get_by_tag("player").pos),
                                                                    15, self.camera.pos+(5, 105), (255,255,255)) 
    def switch_speed(self):
        self.sprint = True

    def m_heal(self,amount):
        for i in self.inventory.items:
            i.damage(amount)

    def draw_inv(self):
        if map_loader.can_openpostmenu: self.inventory.add_item(random.choice(items))
        if map_loader.in_house: self.score += self.inventory.remove_item().cost
        
        if not self.inventory.items:
            return

        start_x, start_y = 10, self.screen.get_height() - 75
        
        for i, item in enumerate(self.inventory.items):
            item_text = f"{i+1}. {item.name} (Dur: {round(item.dur,1)}, Cond: {round(item.cond,1)})"
            self.text_manager.add_text(item_text, 15, self.camera.pos+(start_x, start_y + i * 20), (255, 255, 255))
    def end(self):
        self.running = False
    def end_game(self):
        old_score = self.get_and_write_score()
        self.text_manager.add_text("Счёт:"+str(round(self.score,1))+"Рекорд:"+str(round(old_score,1)),30,(1280/2-300, 720/2-30)+self.camera.pos,(255,255,255))
        self.triggermanager.add_trigger(TimerTrigger(3000,self.end))
        
    def run(self):
        self.running = True
        while self.running:
            self.deltaTime = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.input.update()

            if self.state == "menu":
                self.menu_scene.update()
                self.menu_scene.draw()
                self.camera.pos = pygame.Vector2(0,0)
                self.scene.draw(self.camera)
                self.text_manager.draw()

            elif self.state == "gameplay":
                self.vertical_speed = min(self.vertical_speed + self.gravity * self.deltaTime, 1500)

                self.player.move_with_collisions(
                    0,
                    self.vertical_speed * self.deltaTime,
                    self.objectmanager.get_collidables()
                )

                if self.vertical_speed >= 0:
                    test_rect = self.player.get_rect().move(0, 1)
                    for obj in self.objectmanager.get_collidables():
                        if obj is not self.player and test_rect.colliderect(obj.get_rect()):
                            self.is_on_ground = True
                            break
            



                self.triggermanager.update(self.deltaTime)
                
                self.objectmanager.update_all()
                self.inventory.update()
                for obj, layer in self.objectmanager.getdrawlist():
                    self.scene.add_object(obj, layer)
                screen_w, screen_h = screensize
                px, py = self.player.pos

                cam_x = int(px - screen_w / 2 + self.player.scale[0] / 2)
                cam_y = int(py - screen_h / 2 + self.player.scale[1] / 4)

                self.camera.set_position(cam_x, cam_y)

                

                self.draw_overlay()
                self.draw_inv()
                self.text_manager.add_text("Счёт: "+str(round(self.score,1)),25,self.camera.pos+(1100,20),(255,255,255))
                if map_loader.c == 4:self.end_game()
                self.text_manager.draw()

                if not self.input.is_key_pressed(pygame.K_q):
                    self.hotkeypressed = False


                self.scene.draw(self.camera) 

            self.is_moving = False
            map_loader.reset_globals()
            pygame.display.flip()
