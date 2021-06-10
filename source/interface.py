from settings import TILE, GAP, HEAD, THEMES, DATA, parser, vec
import pygame


class Widget(pygame.Rect):

    def __init__(self, engine, event_handler, dim):
        super().__init__(*dim)
        self.engine = engine
        self.event_handler = event_handler
        self.surface = pygame.Surface(self.size, pygame.SRCALPHA, 32).convert_alpha()

    @property
    def focused(self):
        return self.collidepoint(*self.event_handler.focus)

    @property
    def clicked(self):
        return self.focused and self.event_handler.click[0]

    @property
    def image(self):
        return self.surface

    def render(self, display):
        display.blit(self.image, self)


class Button(Widget):

    def __init__(self, engine, event_handler, dim, color_key):
        super().__init__(engine, event_handler, dim)
        self.color_key = color_key

    @property
    def image(self):
        self.surface.fill(self.engine.graphics["widget"])
        dim = (GAP * 2, GAP * 2, self.width - GAP * 4, self.height - GAP * 4)
        if self.focused:
            pygame.draw.rect(self.surface, self.engine.graphics[self.color_key], dim)
        else:
            pygame.draw.rect(self.surface, self.engine.graphics["text_2"], dim)
        return self.surface


class Switch(Widget):

    IMAGES = []

    def __init__(self, engine, event_handler, pos, label=None, state=False):
        super().__init__(engine, event_handler, (*pos, TILE * 2, TILE))
        self.state = state

        self.label = label
        self.label_pos = pos + vec(self.width // 2, -GAP)

    @property
    def image(self):

        self.surface.fill(self.engine.graphics["widget"])
        pygame.draw.rect(
            self.surface, self.engine.graphics["field"],
            (TILE // 2 - GAP * 2, GAP * 2, GAP * 4, TILE - GAP * 4)
        )

        if self.state:
            text, color, dim = "On", "text_1", (GAP * 2, TILE - GAP * 6, TILE - GAP * 4, GAP * 4)
        else:
            text, color, dim = "Off", "text_2", (GAP * 2, GAP * 2, TILE - GAP * 4, GAP * 4)

        pygame.draw.rect(self.surface, self.engine.graphics[color], dim)
        self.engine.write(text, self.engine.graphics[color], (TILE * 1.5, TILE * 0.6), self.surface)

        return self.surface

    def flip(self):
        self.state = not self.state

    def render(self, display):
        self.last_state = self.state
        if self.clicked:
            self.state = not self.state

        super().render(display)

        if self.label:
            self.engine.write(
                self.label, self.engine.graphics["text_2"],
                self.label_pos, self.engine.display, align="midbottom"
            )


class KeyTooltip:

    def __init__(self, engine, pos):
        self.engine = engine
        self.active = False
        self.images = {}

        for theme in THEMES:
            image = pygame.Surface((TILE * 6, len(parser["KEYS"]) * TILE + GAP * 4))
            image.fill(DATA["colors"][theme]["widget"])

            for i, item in enumerate(parser["KEYS"].items()):
                name, key = item

                name, name_rect = self.engine.write(f"{name} :", DATA["colors"][theme]["text_2"])
                key, key_rect = self.engine.write(str(key), DATA["colors"][theme]["text_3"])

                name_rect.topleft = (GAP * 4, GAP * 2 + i * TILE)
                key_rect.topright = (TILE * 6 - GAP * 4, GAP * 2 + i * TILE)

                image.blit(name, name_rect)
                image.blit(key, key_rect)

            self.images[theme] = image
            self.rect = image.get_rect()

        self.rect.topright = pos

    def render(self, display):
        if self.active:
            display.blit(self.images[self.engine.graphics.theme], self.rect)
