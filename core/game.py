import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pygame
from utils.input import InputHandler
from scene import Scene
from object_manager import ObjectManager
from objects.gameobjects import GameObject
from camera import Camera
from trigger import TriggerManager, ZoneTrigger, KeyTrigger, TimerTrigger
from menu import MenuScene
from utils.map_loader import load_scene_from_json
from settings import *
from text import TextManager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.input = InputHandler()
        self.camera = Camera()
        self.state = "menu"
        self.is_moving = False
        self.last_move = 'd'
        self.deltaTime = 1
        self.player_speed = 3
        self.hotkeypressed = False
        self.debug_mode = False
        self.vertical_speed = 0
        self.gravity = 2000 
        self.jump_power = -700
        self.is_on_ground = False



        self.scene = Scene(screen)
        self.switch_to_menu()

    def switch_to_menu(self):
        self.state = "menu"
        self.camera = Camera()
        self.scene = Scene(self.screen)
        self.text_manager = TextManager(self.scene)
        self.menu_scene = MenuScene(self.scene, self.input, self.switch_to_gameplay)
        

    def jump(self):
        if self.is_on_ground:
            self.vertical_speed = self.jump_power
            self.is_on_ground = False


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

        self.player = GameObject('assets\\playerm2.png', (100, 450), (100, 200),spawnable=True,collidable=True)
        self.player.add_texture('assets\\playerm1.png', (100, 200))
        self.objectmanager.add_object(self.player, 2)

        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_d, lambda: self.move(1), self.input, once=False)
        )
        self.triggermanager.add_trigger(
            KeyTrigger(pygame.K_a, lambda: self.move(-1), self.input, once=False)
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


        load_scene_from_json(
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
        dx = direction * self.player_speed * self.deltaTime
        self.player.move_with_collisions(dx, 0, self.objectmanager.get_collidables())
        if direction != 0:
            if (direction > 0 and self.last_move != 'd') or (direction < 0 and self.last_move != 'a'):
                self.player.flip()
                self.last_move = 'd' if direction > 0 else 'a'
        self.is_moving = direction != 0

    def anim(self):
        if self.is_moving:
            self.player.swap_texture()
        else:
            self.player.active_texture = 0

        for trigger in self.triggermanager.triggers:
            if isinstance(trigger, TimerTrigger) and not trigger.once:
                trigger.reset()

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
                    

        
    def run(self):
        running = True
        while running:
            deltaTime = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.input.update()

            if self.state == "menu":
                self.menu_scene.update()
                self.menu_scene.draw()
                self.camera.pos = pygame.Vector2(0,0)
                self.scene.draw(self.camera)

            elif self.state == "gameplay":
                self.vertical_speed = min(self.vertical_speed + self.gravity * deltaTime, 1500)

                self.player.move_with_collisions(
                    0,
                    self.vertical_speed * deltaTime,
                    self.objectmanager.get_collidables()
                )

                if self.vertical_speed >= 0:
                    test_rect = self.player.get_rect().move(0, 1)
                    for obj in self.objectmanager.get_collidables():
                        if obj is not self.player and test_rect.colliderect(obj.get_rect()):
                            self.is_on_ground = True
                            break
            



                self.triggermanager.update(deltaTime)
                self.text_manager.draw()
                self.objectmanager.update_all()
                for obj, layer in self.objectmanager.getdrawlist():
                    self.scene.add_object(obj, layer)
                screen_w, screen_h = screensize
                px, py = self.player.pos

                cam_x = int(px - screen_w / 2 + self.player.scale[0] / 2)
                cam_y = int(py - screen_h / 2 + self.player.scale[1] / 4)

                self.camera.set_position(cam_x, cam_y)


                self.draw_overlay()
                
                if not self.input.is_key_pressed(pygame.K_q):
                    self.hotkeypressed = False



                self.scene.draw(self.camera) 

            self.is_moving = False
            pygame.display.flip()
