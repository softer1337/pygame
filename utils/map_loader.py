import json
from core.object_manager import ObjectManager
from objects.gameobjects import GameObject
from core.trigger import *
from settings import *
import settings
from enum import Enum
import random

can_openpostmenu = False
in_house = False

def setpostmenu():
    global can_openpostmenu
    can_openpostmenu = True

def setinhouse():
    global in_house
    in_house = True

def reset_globals():
    global can_openpostmenu,in_house
    can_openpostmenu = False
    in_house = False

triggers = {
    "post": ZoneTrigger((1120,620,70,30), pygame.Rect(0, 0, 0, 0), setpostmenu , False),
    "house_1":ZoneTrigger((1300,110,322,609),pygame.Rect(0,0,0,0), setinhouse, True),
    "house_2":ZoneTrigger((1900,110,322,609),pygame.Rect(0,0,0,0), setinhouse, True),
    "house_3":ZoneTrigger((2500,110,322,609),pygame.Rect(0,0,0,0), setinhouse, True),
    "house_4":ZoneTrigger((3100,110,322,609),pygame.Rect(0,0,0,0), setinhouse, True)
}



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
                base_texture = obj["texture"]
                tile_width = 1024
                tiles_count = 4

                for i in range(tiles_count):
                    bg = GameObject(base_texture, (i * tile_width, 0), settings.screensize)
                    object_manager.add_object(bg, 0)

            case ObjectType.WALL:
                pos = obj["pos"]
                size = obj["size"]
                trigger_data = obj.get("trigger")
                collidable = obj["collidable"]
                tag = obj["tag"]
                wall = GameObject(obj["texture"], (pos['x'], pos['y']), (size['width'], size['height']),collidable=collidable,tag=tag)
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
                tag = obj["tag"]

                wall = GameObject('assets\\empty.png', (pos['x'], pos['y']), (size['width'], size['height']),collidable=True,tag=tag)
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
