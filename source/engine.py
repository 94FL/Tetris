import pygame
from audio import Sound
from classes import Field, Next
from interface import Button, Switch, KeyTooltip
from clock import Clock
from events import EventHandler
from audio import Mixer
from settings import DIM, FPS, COLORS, KEYS, FONT, TILE, DELAY, GAP, ACCELERATION, vec


class Engine:

    display = pygame.display.set_mode(DIM["screen"], pygame.NOFRAME)
    IMAGES = None

    def __init__(self):

        Field.generate_images()
        Mixer.set_volume(0.05)

        self.clock = Clock()
        self.logic_timer = self.clock.timer(DELAY, periodic=True)
        self.tick_timer = self.clock.timer(30, periodic=True)
        self.timer = self.clock.timer(30)

        self.event_handler = EventHandler(self.clock, KEYS)
        self.key_tooltip = KeyTooltip(self, DIM["keys_tooltip"])

        self.exit_button = Button(self, self.event_handler, DIM["exit_button"], COLORS["text_1"])
        self.keys_button = Button(self, self.event_handler, DIM["keys_button"], COLORS["text_3"])
        self.shadow_switch = Switch(self, self.event_handler, DIM["shadow_switch"])
        self.music_switch = Switch(self, self.event_handler, DIM["music_switch"])

        self.running = [False, False, False]

        self.reset()
        self.running[1] = True

    def reset(self):
        self.next = Next(self, DIM['next'])
        self.field = Field(self, DIM['field'], self.next())
        self.next_figure = self.next()

        self.logic_timer.modifier = 1

        if self.running[2] and self.music_switch.state:
            Mixer.theme.play(-1)

        self.running = [True, self.running[1], False]

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

        if self.music_switch.altered:
            if self.music_switch.state:
                Mixer.theme.play(-1)
            else:
                Mixer.theme.stop()

        if self.exit_button.clicked:
            self.running[0] = False

        if self.keys_button.clicked:
            self.key_tooltip.active = not self.key_tooltip.active

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
            temp, sound = 0, False
            for i, row in enumerate(self.field.data):
                if row == ['#' for i in range(self.field.cols)]:
                    self.field.del_row(i)
                    temp += 1
                elif 0 not in row and 'X' not in row:
                    sound = True
                    self.field.data[i] = ['X' for i in range(self.field.cols)]
            if sound:
                Mixer.SOUNDS["clear"].play()

            if temp:
                self.score += temp**2 * 100
                self.logic_timer.modifier *= (1 - ACCELERATION)
            for element in self.field.data[0]:
                if element:
                    self.game_over()

    def render(self):
        self.display.fill(COLORS['hud'])
        pygame.draw.rect(self.display, COLORS["widget"], DIM["header"])

        self.field.render(self.display)
        self.next.render(self.display)
        self.exit_button.render(self.display)
        self.keys_button.render(self.display)
        self.shadow_switch.render(self.display)
        self.music_switch.render(self.display)

        text, rect = self.write("Tetris", COLORS["text_2"])
        self.display.blit(text, DIM["header_text"])

        self.write("Next figure", COLORS["text_2"], DIM["next_label"], self.display)
        self.write("Score", COLORS["text_2"], DIM["score"], self.display)
        self.write(str(self.score), COLORS["text_1"], DIM["score"] + vec(0, TILE), self.display, large=True)

        if self.running[2]:
            self.write("GAME OVER", COLORS["text_1"], self.field.rect.center, self.display, large=True)
            self.write('press "r"', COLORS["text_2"], DIM["status"] + vec(0, TILE * 1.5), self.display)
            self.write("to restart", COLORS["text_2"], DIM["status"] + vec(0, TILE * 2.5), self.display)
        elif self.running[1]:
            self.write("PAUSED", COLORS["text_1"], DIM["status"], self.display, large=True)
            self.write('press "p"', COLORS["text_2"], DIM["status"] + vec(0, TILE * 1.5), self.display)
            self.write("to continue", COLORS["text_2"], DIM["status"] + vec(0, TILE * 2.5), self.display)
        else:
            self.write("TETRIS", COLORS["field"], DIM["status"] + vec(0, TILE * 2.5), self.display, large=True)

        self.write("Shadow", COLORS["text_2"], DIM["shadow_label"], self.display)
        self.write("Music", COLORS["text_2"], DIM["music_label"], self.display)

        self.key_tooltip.render(self.display)

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
    def write(text, color, pos=(0, 0), canvas=None, large=False):
        surface = FONT[large].render(text, False, color)
        rect = surface.get_rect()
        rect.center = pos
        if canvas is not None:
            canvas.blit(surface, rect)
        return surface, rect


if __name__ == '__main__':
    pygame.init()
    engine = Engine()
    engine.loop()
    pygame.quit()


# TODO:
#  - egyszerűsítés
#  - gyorsulás és pálya/pont rendszer kidolgozása
#  - high score rendszer
