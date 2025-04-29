import json
import pygame
from utils.input import InputHandler
from core.scene import Scene
from core.object_manager import ObjectManager
from objects.gameobjects import GameObject
from core.camera import Camera
from core.trigger import *
from settings import *
import settings
from assets.triggers import triggers
from enum import Enum
import random


class ObjectType(Enum):
    BG = 'bg'
    WALL = 'wall'
    SPAWNPOINT = 'spawnpoint'
    COLLIDER = 'collider'


def load_scene_from_json(object_manager: ObjectManager, trigger_manager: TriggerManager, path, player: GameObject):
    with open(path, 'r') as jsonf:
        data = json.load(jsonf)

    for obj in data:
        object_type = ObjectType(obj['type'])

        match object_type:
            case ObjectType.BG:
                bg = GameObject(obj['texture'], (0, 0), settings.screensize)
                object_manager.add_object(bg, 0)

            case ObjectType.WALL:
                pos = obj["pos"]
                size = obj["size"]
                trigger_data = obj.get("trigger")
                collidable = obj["collidable"]

                wall = GameObject(obj["texture"], (pos['x'], pos['y']), (size['width'], size['height']),collidable=collidable)
                object_manager.add_object(wall, obj["layer"])

                if trigger_data:
                    trigger_str = trigger_data["name"]
                    if trigger_str in triggers:
                        trigger = triggers[trigger_str]
                        trigger.get_target_rect = player.get_rect
                        trigger_manager.add_trigger(trigger)
                        if settings.mode == "debug" : print(f"[DEBUG] Trigger '{trigger_str}' added")
                    else:
                        print(f"[WARNING] Trigger '{trigger_str}' not found in assets.triggers")
            case ObjectType.SPAWNPOINT:
                pos = obj['pos']
                x, y = pos['x'], pos['y']
                spawnables = [
                    instance
                    for instance, layer in object_manager.objects.values()
                    if getattr(instance, 'spawnable', False)
                ]

                if not spawnables:
                    print(f"[WARNING] No spawnable objects for spawnpoint at {(x,y)}")
                else:
                    chosen = random.choice(spawnables)
                    chosen.pos = (x, y)
                    chosen.spawnable = False
            case ObjectType.COLLIDER:
                pos = obj["pos"]
                size = obj["size"]
                trigger_data = obj.get("trigger")

                wall = GameObject('assets\\empty.png', (pos['x'], pos['y']), (size['width'], size['height']),collidable=True)
                object_manager.add_object(wall, obj["layer"])

                if trigger_data:
                    trigger_str = trigger_data["name"]
                    if trigger_str in triggers:
                        trigger = triggers[trigger_str]
                        trigger.get_target_rect = player.get_rect
                        trigger_manager.add_trigger(trigger)
                        if settings.mode == "debug" : print(f"[DEBUG] Trigger '{trigger_str}' added")
                    else:
                        print(f"[WARNING] Trigger '{trigger_str}' not found in assets.triggers")
