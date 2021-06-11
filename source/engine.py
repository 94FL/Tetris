from ctypes import windll, wintypes, pointer

import pygame
from graphics import Graphics

from audio import Mixer
from classes import Field, Next
from clock import Clock
from events import EventHandler
from interface import Widget, Button, Switch, KeyTooltip
from settings import DIM, FPS, KEYS, FONT, TILE, DELAY, VOLUME, SCORE, MAX_LEVEL, STARTING_LEVEL, \
    KILLER_MODIFIER, vec, parser


class Engine:
    display = pygame.display.set_mode(DIM["screen"], pygame.NOFRAME)
    IMAGES = None
    TITLE = "Tetris"

    def __init__(self):

        Mixer.set_volume(VOLUME)
        self.window_handle = pygame.display.get_wm_info()['window']

        self.graphics = Graphics(self)

        self.clock = Clock()
        self.logic_timer = self.clock.timer(DELAY, periodic=True)
        self.tick_timer = self.clock.timer(30, periodic=True)
        self.timer = self.clock.timer(30)

        self.event_handler = EventHandler(self.clock, KEYS)
        self.key_tooltip = KeyTooltip(self, DIM["keys_tooltip"])

        self.exit_button = Button(self, self.event_handler, DIM["exit_button"], "text_1")
        self.keys_button = Button(self, self.event_handler, DIM["keys_button"], "text_3")
        self.shadow_switch = Switch(self, self.event_handler, DIM["shadow_switch"], "Shadow", state=True)
        self.music_switch = Switch(self, self.event_handler, DIM["music_switch"], "Music")
        self.sound_switch = Switch(self, self.event_handler, DIM["sound_switch"], "Sound")
        self.theme_switch = Switch(self, self.event_handler, DIM["theme_switch"], "Light")
        self.header = Widget(self, self.event_handler, DIM["header"])

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

        self.lines = 0
        self.score = 0
        self.level = min(self.lines // 10 + STARTING_LEVEL, MAX_LEVEL)
        self.logic_timer.modifier = (KILLER_MODIFIER ** (1 / MAX_LEVEL)) ** (self.level - 1)

    def delay(self, time=DELAY * 0.5):
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
        if self.event_handler['reset', 'press'] and self.running[2]:
            self.reset()
        if self.event_handler['theme', 'press']:
            self.theme_switch.flip()

        if not pygame.key.get_focused():  # or not pygame.mouse.get_focused():  # (only for extreme focus mode)
            self.running[1] = True

        if self.music_switch.clicked:
            if self.music_switch.state:
                Mixer.theme.stop()
            else:
                Mixer.theme.play(-1)

        Mixer.enabled = self.sound_switch.state

        if self.exit_button.clicked:
            self.running[0] = False

        if self.keys_button.clicked:
            self.key_tooltip.active = not self.key_tooltip.active

        if self.event_handler.hold[0] and self.header.focused:
            self.drag_window()

        if not any(self.running[1:]):
            if self.event_handler["rotate cw", "press"]:
                self.field.rotate_figure(-1)
            if self.event_handler["rotate ccw", "press"]:
                self.field.rotate_figure(1)
            if self.event_handler["rotate", "press"]:
                self.field.rotate_figure(1)
            if self.event_handler["move left", "press"]:
                self.field.move_figure(vec(-1, 0))
            if self.event_handler["move right", "press"]:
                self.field.move_figure(vec(1, 0))
            if self.event_handler["move down", "press"] and self.timer.query():
                self.timer.reset()
                self.logic_timer.reset()
                self.field.drop_figure()
            if self.event_handler["place", "press"]:
                self.field.place_figure()

    def logic(self):
        if not any(self.running[1:]):
            if self.logic_timer.query():
                self.field.drop_figure(True)
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
                if Mixer.enabled:
                    Mixer.SOUNDS["clear"].play()

            # progress
            if temp:
                self.lines += temp
                self.level = min(self.lines // 10 + STARTING_LEVEL, MAX_LEVEL)
                self.score += SCORE[temp] * self.level
                self.logic_timer.modifier = (KILLER_MODIFIER ** (1 / MAX_LEVEL)) ** (self.level - 1)

            for element in self.field.data[0]:
                if element:
                    self.game_over()

    def render(self):
        self.display.fill(self.graphics['hud'])
        pygame.draw.rect(self.display, self.graphics["widget"], self.header)

        self.field.render(self.display)
        self.next.render(self.display)
        self.exit_button.render(self.display)
        self.keys_button.render(self.display)
        self.shadow_switch.render(self.display)
        self.music_switch.render(self.display)
        self.sound_switch.render(self.display)
        self.theme_switch.render(self.display)

        text, rect = self.write(self.TITLE, self.graphics["text_2"])
        self.display.blit(text, DIM["header_text"])

        self.write("Next figure", self.graphics["text_2"], DIM["next_label"], self.display)
        self.write("Score", self.graphics["text_2"], DIM["score"], self.display)
        self.write(str(self.score), self.graphics["text_1"], DIM["score"] + vec(0, TILE), self.display, True)

        self.write("Level", self.graphics["text_2"], DIM["level"], self.display)
        self.write(str(self.level), self.graphics["text_1"], DIM["level"] + vec(0, TILE), self.display, True)

        if self.running[2]:
            gameo_label = f'press "{str(parser.get("KEYS", "reset"))}"'
            self.write("GAME OVER", self.graphics["text_1"], DIM["label"], self.display, True)
            self.write(gameo_label, self.graphics["text_2"], DIM["label"] + vec(0, TILE * 1.5), self.display)
            self.write("to restart", self.graphics["text_2"], DIM["label"] + vec(0, TILE * 2.5), self.display)
        elif self.running[1]:
            pause_label = f'press "{str(parser.get("KEYS", "pause"))}"'
            self.write("PAUSED", self.graphics["text_1"], DIM["label"], self.display, True)
            self.write(pause_label, self.graphics["text_2"], DIM["label"] + vec(0, TILE * 1.5), self.display)
            self.write("to continue", self.graphics["text_2"], DIM["label"] + vec(0, TILE * 2.5), self.display)

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
    def write(text, color, pos=(0, 0), canvas=None, large=False, align="center"):
        surface = FONT[large].render(text, False, color)
        rect = surface.get_rect()
        setattr(rect, align, pos)
        if canvas is not None:
            canvas.blit(surface, rect)
        return surface, rect

    def drag_window(self):
        pos = wintypes.POINT()
        windll.user32.GetCursorPos(pointer(pos))

        dx, dy = self.event_handler.drag[0]
        cx, cy = pos.x, pos.y

        x, y = int(cx - dx), int(cy - dy)
        windll.user32.MoveWindow(self.window_handle, x, y, *DIM["screen"], True)


if __name__ == '__main__':
    pygame.init()
    engine = Engine()
    engine.loop()
    pygame.quit()

# TODO:
#  - egyszerűsítés
#  - high score rendszer
#  - dinamikus színek
