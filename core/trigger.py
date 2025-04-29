import pygame
import settings

class TriggerManager:
    def __init__(self):
        self.triggers = []
        self.activated = []

    def add_trigger(self, trigger):
        self.triggers.append(trigger)

    def remove_trigger(self, trigger):
        if trigger in self.triggers:
            self.triggers.remove(trigger)

    def update(self, dt):
        self.activated.clear()

        for trigger in self.triggers:
            trigger.update(dt)
            trigger.check()
            if trigger.triggered:
                self.activated.append(trigger)

    def reset_all(self):
        for trigger in self.triggers:
            trigger.reset()


    # def draw_all(self, screen, camera=None):
    #     for trigger in self.triggers:
    #         # draw ZoneTriggers with camera offset
    #         if hasattr(trigger, 'rect') and camera:
    #             trigger.draw(screen, camera)
            # else:
            #     trigger.draw(screen)


class Trigger:
    def __init__(self, callback, args=None, kwargs=None, once=True, color=(255, 0, 0)):
        self.callback = callback
        self.args = args if args else ()
        self.kwargs = kwargs if kwargs else {}
        self.once = once
        self.triggered = False
        self.color = color

    def activate(self):
        name = getattr(self.callback, '__name__', str(self.callback))

        if settings.mode == "debug":print(f"[TRIGGER] Activated {name} at {getattr(self, 'rect', None)}")
        if not self.once or not self.triggered:
            self.callback(*self.args, **self.kwargs)
            self.triggered = True

    def reset(self):
        if not self.once:
            self.triggered = False

    def check(self):
        pass

    def draw(self, screen):
        pass


class ZoneTrigger(Trigger):
    def __init__(self, rect, target_rect, callback=None, once=True):
        super().__init__(callback, once=once)
        self.rect = pygame.Rect(rect)
        self.t_rect = target_rect
        self.get_target_rect = None
        self.color = (255, 0, 0)

    def update(self, dt):
        if self.get_target_rect:
            self.t_rect = self.get_target_rect()

    def check(self):
        if self.rect.colliderect(self.t_rect):
            self.activate()

    def draw(self, screen, camera):
        outline_color = (0, 255, 0) if self.triggered else self.color
        draw_pos = camera.apply((self.rect.x, self.rect.y))
        draw_rect = pygame.Rect(draw_pos, (self.rect.width, self.rect.height))
        pygame.draw.rect(screen, outline_color, draw_rect, 2)
        center_screen = camera.apply(self.rect.center)
        pygame.draw.circle(screen, (0, 0, 255), center_screen, 5)


class KeyTrigger(Trigger):
    def __init__(self, key, callback, input_handler, args=None, kwargs=None, once=True, color=(255, 0, 0)):
        super().__init__(callback, args, kwargs, once, color)
        self.key = key
        self.input_handler = input_handler

    def check(self):
        if self.input_handler.is_key_pressed(self.key):
            self.activate()
        else:
            self.reset()

    def update(self, dt):
        pass


class TimerTrigger(Trigger):
    def __init__(self, delay_ms, callback, args=None, kwargs=None, once=True, color=(255, 0, 0)):
        super().__init__(callback, args, kwargs, once, color)
        self.delay_ms = delay_ms
        self.start_time = pygame.time.get_ticks()

    def check(self):
        now = pygame.time.get_ticks()
        if now - self.start_time >= self.delay_ms:
            self.activate()

    def reset(self):
        super().reset()
        if not self.once:
            self.start_time = pygame.time.get_ticks()

    def update(self, dt):
        pass
