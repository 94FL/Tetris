import random

import pygame
from settings import FIGURE_DATA, FIGURE_NAMES, TILE, COLORS, GAP, vec
from audio import Mixer


class Matrix:

    def __init__(self, cols, rows):
        self.cols = cols
        self.rows = rows
        self.data = [[0 for _ in range(cols)] for __ in range(rows)]
        self.index = [0, 0]

    def __getitem__(self, index: (int, int)) -> int:
        x, y = index
        return self.data[int(y)][int(x)]

    def __setitem__(self, index: (int, int), item):
        x, y = index
        self.data[int(y)][int(x)] = item

    def __iter__(self):
        self.index = [0, 0]
        return self

    def __next__(self) -> (int, int, str):
        self.index[0] += 1
        if self.index[0] > self.cols:
            self.index[0] = 0
            self.index[1] += 1
            if self.index[1] > self.rows:
                raise StopIteration
        return self.index[0] - 1, self.index[1] - 1, self[self.index[0] - 1, self.index[1] - 1]

    def del_row(self, row):
        del self.data[row]
        self.data.insert(0, [0 for _ in range(self.cols)])


class Field(pygame.Surface, Matrix):

    FIGURES = FIGURE_NAMES + ("X", "#")
    SHINE_SHAPE = ((1, 1), (3, 1), (3, 2), (2, 2), (2, 3), (1, 3))
    IMAGES = {}

    def __init__(self, engine, dim, _next):
        pygame.Surface.__init__(self, (dim[2] * TILE, dim[3] * TILE))
        Matrix.__init__(self, dim[2], dim[3])
        self.engine = engine
        self.dim = dim
        self.rect = self.get_rect()
        self.rect.topleft = dim[:2]
        self.figure = Figure(self)
        self.figure.reset(_next)

        self.background = pygame.Surface((dim[2] * TILE, dim[3] * TILE))

    @classmethod
    def generate_images(cls):
        for figure in Field.FIGURES:
            image = pygame.Surface((TILE, TILE), pygame.SRCALPHA, 32).convert_alpha()
            temp = image.copy()
            temp.fill((160, 160, 160))
            pygame.draw.rect(image, COLORS[figure], (GAP, GAP, TILE - GAP * 2, TILE - GAP * 2))
            pygame.draw.polygon(temp, (255, 255, 255), [[c * GAP * 2 for c in p] for p in Field.SHINE_SHAPE])

            image.blit(temp, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            cls.IMAGES[figure] = image

    def collide_figure(self, sides=True, pos=0):
        for x, y in self.figure:
            if sides and x < 0:
                return 2
            if sides and x >= self.cols:
                return 3
            if y + pos >= self.rows or self[x, y + pos] or x < 0 or x >= self.cols:
                return 1
        return 0

    @Mixer.play("low blip")
    def drop_figure(self):
        self.figure.pos += vec(0, 1)
        if self.collide_figure(False):
            self.figure.pos += vec(0, -1)
            self.merge_figure()

    @Mixer.play("blip")
    def move_figure(self, vector):
        self.figure.pos += vector
        if self.collide_figure():
            self.figure.pos -= vector

    @Mixer.play("blip")
    def rotate_figure(self, direction):
        if self.figure.pos[1] == 0:
            self.figure.pos[1] = 1

        temp = self.figure.orient
        self.figure.orient += direction

        if self.figure.orient >= len(self.figure.data):
            self.figure.orient = 0
        if self.figure.orient < 0:
            self.figure.orient = len(self.figure.data) - 1

        if self.collide_figure() == 1:
            self.figure.orient = temp
        if self.collide_figure() == 2:
            self.move_figure(vec((1, 2)[self.figure.figure == "I"], 0))
        if self.collide_figure() == 3:
            self.move_figure(vec(-1, 0))

    def place_figure(self):
        self.figure.pos += vec(0, self.height())
        self.merge_figure()

    @Mixer.play("high blip")
    def merge_figure(self):
        for x, y in self.figure:
            self[x, y] = self.figure.figure
        self.figure.reset(self.engine.next_figure)

        if self.collide_figure() == 2:
            self.move_figure(vec((1, 2)[self.figure.figure == "I"], 0))
        if self.collide_figure() == 3:
            self.move_figure(vec(-1, 0))

        self.engine.delay()
        self.engine.next_figure = self.engine.next()

    def render(self, surface):
        self.fill(COLORS['field'])
        height = self.height()

        for x, y, tile in self:
            if tile:
                self.blit(Field.IMAGES[tile], (x * TILE, y * TILE))

        for x, y in self.figure:
            self.blit(Field.IMAGES[self.figure.figure], (x * TILE, y * TILE))

            if self.engine.shadow_switch.state:
                rect = pygame.Rect(x * TILE + GAP, (y + height) * TILE + GAP, TILE - GAP * 2, TILE - GAP * 2)
                pygame.draw.rect(self, COLORS["shadow"], rect, 2)

        surface.blit(self, self.rect)

    def height(self, distance=0):
        while not self.collide_figure(pos=distance):
            distance += 1
        return distance - 1


class Figure:

    def __init__(self, engine):
        self.data = None
        self.figure = None
        self.engine = engine
        self.orient = 0
        self.index = 0
        self.pos = vec(5, 0)

    def __getitem__(self, index):
        return self.data[self.orient][index]

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        self.index += 1
        if self.index > 4:
            raise StopIteration
        x, y = vec(self[self.index - 1]) + self.pos
        return x, y

    def reset(self, shape):
        self.pos.y = 0
        self.orient = 0
        self.data = FIGURE_DATA[shape][:]
        self.figure = shape


class Next:
    POS = {
        'O': (1.5, 1.5),
        'I': (2.5, 2),
        'T': (2, 1.5),
        'L': (2, 1.5),
        'J': (2, 1.5),
        'S': (2, 1.5),
        'Z': (2, 1.5)
    }

    def __init__(self, engine, pos):
        self.engine = engine
        self.pos = pos
        self.container = list(FIGURE_NAMES[:])

    def __call__(self):
        figure = random.choice(self.container)
        self.container.remove(figure)
        if not self.container:
            self.container = list(FIGURE_NAMES[:])
        return figure

    def render(self, surface):
        figure = self.engine.next_figure
        array = [vec(element) + vec(Next.POS[figure]) for element in FIGURE_DATA[figure][0]]
        for x, y in array:
            surface.blit(Field.IMAGES[figure], vec(x * TILE, y * TILE) + self.pos)


class Switch(pygame.Rect):

    IMAGES = []

    def __init__(self, engine, event_handler, pos):
        super().__init__(*pos, TILE * 2, TILE)
        self.engine = engine
        self.event_handler = event_handler
        self.state = False
        self.last_state = False

    @property
    def focused(self):
        return self.collidepoint(*self.event_handler.focus)

    @property
    def clicked(self):
        return self.focused and self.event_handler.click[0]

    @property
    def altered(self):
        return int(self.state) - int(self.last_state)

    @classmethod
    def generate_images(cls, write):
        base = pygame.Surface((TILE * 2, TILE), pygame.SRCALPHA, 32).convert_alpha()
        base.fill(COLORS["widget"])
        pygame.draw.rect(base, COLORS["field"], (TILE // 2 - GAP * 2, GAP * 2, GAP * 4, TILE - GAP * 4))

        on_active = base.copy()
        on_passive = base.copy()
        off_active = base.copy()
        off_passive = base.copy()

        pygame.draw.rect(on_active, COLORS["text_1"], (GAP * 2, TILE - GAP * 6, TILE - GAP * 4, GAP * 4))
        pygame.draw.rect(on_passive, COLORS["text_1"], (GAP * 2, TILE - GAP * 6, TILE - GAP * 4, GAP * 4))
        pygame.draw.rect(off_active, COLORS["text_2"], (GAP * 2, GAP * 2, TILE - GAP * 4, GAP * 4))
        pygame.draw.rect(off_passive, COLORS["text_2"], (GAP * 2, GAP * 2, TILE - GAP * 4, GAP * 4))

        write("On", (TILE * 1.5, TILE * 0.6), COLORS["text_1"], on_active)
        write("On", (TILE * 1.5, TILE * 0.6), COLORS["text_1"], on_passive)
        write("Off", (TILE * 1.5, TILE * 0.6), COLORS["text_2"], off_active)
        write("Off", (TILE * 1.5, TILE * 0.6), COLORS["text_2"], off_passive)

        cls.IMAGES = ((off_passive, on_passive), (off_active, on_active))

    def render(self, display):
        self.last_state = self.state
        if self.clicked:
            self.state = not self.state

        display.blit(Switch.IMAGES[self.focused][self.state], self)
