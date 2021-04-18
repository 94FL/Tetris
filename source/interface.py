from settings import TILE, COLORS, GAP, HEAD, parser, vec
import pygame


class Widget(pygame.Rect):

    def __init__(self, engine, event_handler, dim):
        super().__init__(*dim)
        self.engine = engine
        self.event_handler = event_handler

        self.images = self.generate_images()

    @property
    def focused(self):
        return self.collidepoint(*self.event_handler.focus)

    @property
    def clicked(self):
        return self.focused and self.event_handler.click[0]

    def generate_images(self):
        return None


class Button(Widget):

    def __init__(self, engine, event_handler, dim, color):
        self.color = color
        super().__init__(engine, event_handler, dim)

    def generate_images(self):
        base = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
        base.fill(COLORS["widget"])

        active = base.copy()
        passive = base.copy()

        pygame.draw.rect(active, self.color, (GAP * 2, GAP * 2, self.width - GAP * 4, self.height - GAP * 4))
        pygame.draw.rect(passive, COLORS["text_2"], (GAP * 2, GAP * 2, self.width - GAP * 4, self.height - GAP * 4))

        return passive, active

    def render(self, display):
        display.blit(self.images[self.focused], self)


class Switch(Widget):

    IMAGES = []

    def __init__(self, engine, event_handler, pos, label=None, state=False):
        super().__init__(engine, event_handler, (*pos, TILE * 2, TILE))
        self.state = state

        self.label = label
        self.label_pos = pos + vec(self.width // 2, -GAP)

    def generate_images(self):
        base = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()
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

        self.engine.write("On", COLORS["text_1"], (TILE * 1.5, TILE * 0.6), on_active)
        self.engine.write("On", COLORS["text_1"], (TILE * 1.5, TILE * 0.6), on_passive)
        self.engine.write("Off", COLORS["text_2"], (TILE * 1.5, TILE * 0.6), off_active)
        self.engine.write("Off", COLORS["text_2"], (TILE * 1.5, TILE * 0.6), off_passive)

        return (off_passive, on_passive), (off_active, on_active)

    def render(self, display):
        self.last_state = self.state
        if self.clicked:
            self.state = not self.state

        display.blit(self.images[self.focused][self.state], self)

        if self.label:
            self.engine.write(self.label, COLORS["text_2"], self.label_pos, self.engine.display, align="midbottom")


class KeyTooltip(pygame.Surface):

    def __init__(self, engine, pos):
        super().__init__((TILE * 6, len(parser["KEYS"]) * TILE + GAP * 4))
        print(len(parser["KEYS"]))
        self.rect = self.get_rect()
        self.rect.topright = pos

        self.engine = engine
        self.active = False

        self.fill(COLORS["widget"])
        for i, item in enumerate(parser["KEYS"].items()):
            name, key = item

            name, name_rect = self.engine.write(f"{name} :", COLORS["text_2"])
            key, key_rect = self.engine.write(str(key), COLORS["text_3"])

            name_rect.topleft = (GAP * 4, GAP * 2 + i * TILE)
            key_rect.topright = (TILE * 6 - GAP * 4, GAP * 2 + i * TILE)

            self.blit(name, name_rect)
            self.blit(key, key_rect)

    def render(self, display):
        if self.active:
            display.blit(self, self.rect)
