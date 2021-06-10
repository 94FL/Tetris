import pygame
from settings import FIGURE_NAMES, TILE, GAP, THEMES, DATA


class Graphics:

    FIGURES = FIGURE_NAMES + ("X", "#")

    def __init__(self, engine):
        self.engine = engine
        self._data = DATA["colors"].copy()

        for theme in THEMES:
            for figure in self.FIGURES:
                image = pygame.Surface((TILE, TILE), pygame.SRCALPHA, 32).convert_alpha()
                pygame.draw.rect(image, self._data[theme][figure], (GAP, GAP, TILE - GAP * 2, TILE - GAP * 2))
                self._data[theme][figure] = image

    def __getitem__(self, key):
        return self._data[self.theme][key]

    @property
    def theme(self):
        return THEMES[self.engine.theme_switch.state]
