import os
from functools import wraps

import pygame
from settings import SOUND_DATA, PATH

pygame.mixer.init()


class Sound(pygame.mixer.Sound):

    def __init__(self, filename, volume=0.1):
        super().__init__(os.path.join(PATH["audio"], filename))
        self.set_volume(volume)


class Mixer:

    SOUNDS = {name: Sound(filename) for name, filename in SOUND_DATA.items()}
    theme = pygame.mixer.music
    theme.load(os.path.join(PATH["audio"], SOUND_DATA["theme"]))

    @classmethod
    def play(cls, key):
        sound = cls.SOUNDS[key]

        def outer_wrapper(function):
            @wraps(function)
            def inner_wrapper(self, *args, **kwargs):
                sound.play()
                return function(self, *args, **kwargs)
            return inner_wrapper
        return outer_wrapper

    @classmethod
    def set_volume(cls, value, sounds=SOUNDS.keys()):
        cls.theme.set_volume(value)
        for key in sounds:
            cls.SOUNDS[key].set_volume(value)
