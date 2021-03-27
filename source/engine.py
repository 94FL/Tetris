import pygame
from audio import Sound
from classes import Field, Next, Switch
from clock import Clock
from events import EventHandler
from audio import Mixer
from settings import DIM, FPS, COLORS, KEYS, FONT, TILE, DELAY, vec


class Engine:
    display = pygame.display.set_mode(DIM["screen"])
    pygame.display.set_caption("TETRIS")
    IMAGES = None

    def __init__(self):

        Field.generate_images()
        Switch.generate_images(self.write)
        Mixer.set_volume(0.1)

        self.clock = Clock()
        self.logic_timer = self.clock.timer(DELAY, periodic=True)
        self.tick_timer = self.clock.timer(30, periodic=True)
        self.timer = self.clock.timer(30)

        self.event_handler = EventHandler(self.clock, KEYS)

        self.shadow_switch = Switch(self, self.event_handler, DIM["shadow_switch"])
        self.music_switch = Switch(self, self.event_handler, DIM["music_switch"])

        self.running = [True, False, False]

        self.reset()
        self.running[1] = True

    def reset(self):
        self.next = Next(self, DIM['next'])
        self.field = Field(self, DIM['field'], self.next())
        self.next_figure = self.next()

        if self.running[2] and self.music_switch.state:
            Mixer.theme.play(-1)

        self.running = [True, False, False]

        self.score = 0

    def delay(self, time=DELAY):
        self.logic_timer.delay(time)
        self.timer.delay(time)

    def events(self):
        self.event_handler.update()
        if self.event_handler['exit']:
            self.running[0] = False
        if self.event_handler['exit', 'press']:
            self.running[0] = False
        if self.event_handler['pause', 'press']:
            self.running[1] = not self.running[1]
        if self.event_handler['reset', 'press']:
            self.reset()

        if self.music_switch.altered == 1:
            Mixer.theme.play(-1)
        elif self.music_switch.altered == -1:
            Mixer.theme.stop()

        if not any(self.running[1:]):
            if self.event_handler["rotate cw", "press"]:
                self.field.rotate_figure(1)
            if self.event_handler["rotate ccw", "press"]:
                self.field.rotate_figure(-1)
            if self.event_handler["rotate", "press"]:
                self.field.rotate_figure(1)
            if self.event_handler["move left", "press"]:
                self.field.move_figure(vec(-1, 0))
            if self.event_handler["move right", "press"]:
                self.field.move_figure(vec(1, 0))
            if self.event_handler["move down", "press"] and self.timer.query():
                self.timer.reset()
                self.field.drop_figure()
            if self.event_handler["place", "press"]:
                self.field.place_figure()

    def logic(self):
        if not any(self.running[1:]):
            if self.logic_timer.query():
                self.field.drop_figure()
            if self.tick_timer.query():
                for i, row in enumerate(self.field.data):
                    for j in range(len(row)):
                        if self.field[j, i] == 'X':
                            self.field[j, i] = '#'
                            break
            temp = 0
            for i, row in enumerate(self.field.data):
                if row == ['#' for i in range(self.field.cols)]:
                    self.field.del_row(i)
                    temp += 1
                elif not (0 in row) and not ('X' in row):
                    Mixer.SOUNDS["clear"].play()
                    self.field.data[i] = ['X' for i in range(self.field.cols)]
            if temp:
                self.score += temp**2 * 100
            for element in self.field.data[0]:
                if element:
                    self.game_over()

    def render(self):
        self.display.fill(COLORS['hud'])

        self.field.render(self.display)
        self.next.render(self.display)
        self.shadow_switch.render(self.display)
        self.music_switch.render(self.display)

        self.write("Score", DIM["score"], COLORS["text_2"])
        self.write(str(self.score), DIM["score"] + vec(0, TILE), COLORS["text_1"], large=True)

        if self.running[2]:
            self.write("GAME OVER", self.field.rect.center, COLORS["text_1"], large=True)
            self.write('press "r"', DIM["status"] + vec(0, TILE * 2), COLORS["text_2"])
            self.write("to restart", DIM["status"] + vec(0, TILE * 3), COLORS["text_2"])
        elif self.running[1]:
            self.write("PAUSED", DIM["status"], COLORS["text_1"], large=True)
            self.write('press "p"', DIM["status"] + vec(0, TILE * 2), COLORS["text_2"])
            self.write("to continue", DIM["status"] + vec(0, TILE * 3), COLORS["text_2"])
        else:
            self.write("TETRIS", DIM["status"] + vec(0, TILE * 3), COLORS["field"], large=True)

        self.write("Shadow", DIM["shadow_label"], COLORS["text_2"])
        self.write("Music", DIM["music_label"], COLORS["text_2"])

        pygame.display.flip()

    def loop(self):
        self.running[0] = True
        while self.running[0]:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.logic()
            self.render()

    @Mixer.play("fail")
    def game_over(self):
        Mixer.theme.stop()
        self.running[2] = True

    @staticmethod
    def write(text, pos, color, canvas=display, large=False):
        surface = FONT[large].render(text, False, color)
        rect = surface.get_rect()
        rect.center = pos
        canvas.blit(surface, rect)


if __name__ == '__main__':
    pygame.init()
    engine = Engine()
    engine.loop()
    pygame.quit()


# TODO:
#  - egyszerűsítés
#  - gyorsulás
