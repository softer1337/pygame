import pygame
from objects.gameobjects import GameObject

class ObjectManager():
    def __init__(self):
        self.objects = {}
    def add_object(self, obj, layer: int):
        obj_id = id(obj)
        self.objects[obj_id] = (obj, layer)
        return obj_id
    def remove_object(self, obj):
        obj_id = id(obj) 
        if obj_id in self.objects:
            del self.objects[obj_id]
    def update_all(self):
        for obj, _ in self.objects.values():
            obj.update()
    def getdrawlist(self):
        return [(obj, layer) for obj, layer in self.objects.values()]
    def get_collidables(self):
        return [obj for obj, layer in self.objects.values() if obj.collidable]
    def get_by_tag(self, tag: str) -> GameObject:
        for obj, _ in self.objects.values():
            if getattr(obj, "tag", None) == tag:
                return obj
        return None
