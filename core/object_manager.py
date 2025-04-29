import pygame

class ObjectManager():
    def __init__(self):
        self.objects = {}
    def add_object(self, obj, layer: int):
        obj_id = id(obj)
        self.objects[obj_id] = (obj, layer)
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

