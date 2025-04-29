import pygame

class GameObject():
    def __init__(self, img_dir=None, pos=(0, 0), scale=(0, 0), surface=None,spawnable=False,collidable=False):
        self.scale = scale
        self.pos = pos
        self.sx = 0
        self.sy = 0
        self.textures = []
        self.spawnable = spawnable
        self.collidable = collidable

        if surface:
            self.img = surface 
        else:
            self.img = pygame.transform.scale(pygame.image.load(img_dir).convert_alpha(), scale)

        self.textures.append(self.img)
        self.active_texture = 0
        self.image_rect = self.textures[self.active_texture].get_rect(topleft=self.pos)

    def add_texture(self, texture_dir, scale):
        texture = pygame.transform.scale(pygame.image.load(texture_dir).convert_alpha(), scale)
        self.textures.append(texture)

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
        return pygame.Rect(self.pos[0], self.pos[1], self.scale[0], self.scale[1])
    def collides_with(self, other):
        return self.get_rect().colliderect(other.get_rect())

