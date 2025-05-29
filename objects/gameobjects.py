import pygame,random

class GameObject():
    def __init__(self, img_dir=None, pos=(0, 0), scale=(0, 0), surface=None,spawnable=False,collidable=False,tag='',metadata=[]):
        self.scale = scale
        self.pos = pos
        self.sx = 0
        self.sy = 0
        self.textures = []
        self.spawnable = spawnable
        self.collidable = collidable
        self.tag = tag
        self.metadata = metadata
        if surface:
            self.img = surface 
        else:
            if self.scale != (0,0):
                self.img = pygame.transform.scale(pygame.image.load(img_dir).convert_alpha(), scale)
            else:
                self.img = pygame.image.load(img_dir).convert_alpha()

        self.textures.append(self.img)
        self.active_texture = 0
        self.image_rect = self.textures[self.active_texture].get_rect(topleft=self.pos)

    def add_texture(self, texture_dir, scale=(0,0)):
        if self.scale != (0,0):
            self.texture = pygame.transform.scale(pygame.image.load(texture_dir).convert_alpha(), scale)
        else:
            self.texture = pygame.image.load(texture_dir).convert_alpha()
        self.textures.append(self.texture)

    def swap_texture(self):
        self.active_texture = (self.active_texture + 1) % len(self.textures)

    def flip(self):
        self.textures = [pygame.transform.flip(texture, True, False) for texture in self.textures]

    def set_speed(self, sx, sy):
        self.sx = sx
        self.sy = sy

    def move_with_collisions(self, dx, dy, collidables):
        original_rect = self.get_rect()

        new_x = original_rect.x + dx
        test_rect = original_rect.copy()
        test_rect.x = new_x
        
        collided = False
        for obj in collidables:
            if obj is self or not obj.collidable:
                continue
                
            if test_rect.colliderect(obj.get_rect()):
                if dx > 0:
                    new_x = obj.get_rect().left - original_rect.width
                elif dx < 0:  
                    new_x = obj.get_rect().right
                collided = True
                break

        new_y = original_rect.y + dy
        test_rect.x = new_x
        test_rect.y = new_y
        
        for obj in collidables:
            if obj is self or not obj.collidable:
                continue
                
            if test_rect.colliderect(obj.get_rect()):
                if dy > 0:  
                    new_y = obj.get_rect().top - original_rect.height
                    self.vertical_speed = 0
                    self.is_on_ground = True
                elif dy < 0:  
                    new_y = obj.get_rect().bottom
                    self.vertical_speed = 0
                break

        self.pos = (new_x, new_y)
        self.image_rect.topleft = self.pos



    def update(self):
        self.pos = (self.pos[0] + self.sx, self.pos[1] + self.sy)
        self.image_rect.topleft = self.pos

    def draw(self, screen, camera):
        screen_pos = camera.apply(self.pos)
        screen_pos = (int(screen_pos[0]), int(screen_pos[1])) 
        screen.blit(self.textures[self.active_texture], screen_pos)

    def get_rect(self):
        if self.scale != (0, 0):
            width, height = self.scale
        else:
            width, height = self.textures[self.active_texture].get_size()
        return pygame.Rect(self.pos[0], self.pos[1], width, height)

    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())

class Item():
    def __init__(self, name, cost, dur):
        self.name = name
        self.cost = cost
        self.dur = dur 
        self.cond = 100  
    
    def damage(self, force):
        self.dur -= force
        self.cond = max(0, (self.dur / (self.dur + force)) * 100)
        self.cost *= self.cond/100
    def get_data(self):
        return f"{self.name} (Цена: {self.cost}, Сост.: {self.cond}%, Прочн.: {self.dur})"
    def __str__(self):
        return self.name   
class Inventory():
    def __init__(self, max_size=3):
        self.items = []
        self.max_size = max_size
    
    def add_item(self, item: Item):
        if len(self.items) < self.max_size:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self) -> Item:
        to_rem = random.choice(self.items)
        self.items.remove(to_rem)
        return to_rem
    
    def update(self):
        for item in self.items[:]: 
            if item.cond <= 0 or item.dur <= 0:
                self.items.remove(item)
    
    def set_max_size(self, new_size):
        self.max_size = new_size
        if len(self.items) > self.max_size:
            self.items = self.items[:self.max_size]
    
    def __str__(self):
        return "\n".join(f"{i+1}. {item.get_data()}" for i, item in enumerate(self.items))