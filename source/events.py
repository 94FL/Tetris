import pygame
from settings import KEY_DELAYS, vec


class Key:

    def __init__(self, key, repeat, clock):
        self.key = key
        self.clock = clock
        self.pressed = False
        self.holded = False
        self.statemark = 0
        self.repeat = repeat[0]
        self.signal = clock.timer(repeat[1], periodic=True)

    def __getitem__(self, mode):
        if mode == 'press':
            return self.pressed
        elif mode == 'hold':
            return self.holded

    def update(self, hold, now):
        if hold[self.key] - self.holded == 1:
            self.pressed = True
            self.statemark = now
        elif hold[self.key]:
            if now - self.repeat > self.statemark:
                self.pressed = self.signal.query()
            else:
                self.pressed = False
        else:
            self.pressed = False

        self.holded = hold[self.key]


class EventHandler:

    def __init__(self, clock, keys):
        self.clock = clock
        self.keys = {key: Key(keys[key], delay, clock) for key, delay in KEY_DELAYS.items()}
        self.hold = [0, 0, 0]
        self.click = [0, 0, 0]
        self.events = None
        self.temp = self.click[:]
        self.drag = [vec(0, 0), vec(0, 0)]
        self.now = 0

        self.focus = vec(pygame.mouse.get_pos())
        self.last_focus = vec(pygame.mouse.get_pos())

    def focused(self, rect, carrier=None):
        x, y = self.focus
        if carrier is not None:
            x, y = x - carrier.left, y - carrier.top
        return rect.left < x < rect.right and rect.top < y < rect.bottom

    def update(self):
        self.events = pygame.event.get()
        hold = pygame.key.get_pressed()
        self.now = self.clock.now

        self.focus = vec(pygame.mouse.get_pos())
        self.hold = pygame.mouse.get_pressed()

        if not self.hold[0]:
            self.drag[0] = vec(self.focus)
        self.drag[1] = vec(self.focus)

        for key in self.keys.values():
            key.update(hold, self.now)
        self.click = [current - last == 1 for current, last in zip(self.hold, self.temp)]
        self.temp = self.hold[:]

    def __getitem__(self, key_mode):
        if key_mode == 'exit':
            return any(event.type == pygame.QUIT for event in self.events)
        else:
            key, mode = key_mode
            return self.keys[key][mode]
