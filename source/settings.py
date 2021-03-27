import json
import os
from configparser import ConfigParser
from ctypes import windll

import pygame

vec = pygame.math.Vector2
windll.user32.SetProcessDPIAware()

SOURCE_PATH = os.path.dirname(__file__)
ROOT = os.path.split(SOURCE_PATH)[0]

FPS = 60
SCORE = (0, 4, 10, 30, 120)

PATH = {
    "data": os.path.join(ROOT, "data"),
    "datafile": os.path.join(ROOT, "data", "data.json"),
    "config": os.path.join(ROOT, "data", "config.ini"),
    "font": os.path.join(ROOT, "data", "font.ttf"),
    "audio": os.path.join(ROOT, "data", "audio"),
    "graphics": os.path.join(ROOT, "graphics"),
    "source": SOURCE_PATH,
}

parser = ConfigParser()
parser.read(PATH["config"])

KEYS = {key: pygame.key.key_code(parser.get("KEYS", key)) for key in parser["KEYS"]}

DELAY = parser.getint("SETTINGS", "period")
TILE = parser.getint("SETTINGS", "tile size")
ACCELERATION = parser.getfloat("SETTINGS", "acceleration")

GAP = TILE // 12
FIELD = 10, 20
HEAD = int(TILE * 0.8)

DIM = {
    "screen": (TILE * (FIELD[0] + 5), TILE * FIELD[1] + HEAD),
    "field": (0, HEAD, *FIELD),
    "next": (TILE * FIELD[0], TILE // 2 + HEAD),
    "next_label": (TILE * (FIELD[0] + 2.5), TILE + HEAD),
    "score": (TILE * (FIELD[0] + 2.5), TILE * 6 + HEAD),
    "shadow_label": (TILE * (FIELD[0] + 2.5), TILE * 9.5 + HEAD),
    "shadow_switch": (TILE * (FIELD[0] + 1.5), TILE * 10 + HEAD),
    "music_label": (TILE * (FIELD[0] + 2.5), TILE * 12.5 + HEAD),
    "music_switch": (TILE * (FIELD[0] + 1.5), TILE * 13 + HEAD),
    "status": (TILE * (FIELD[0] + 2.5), TILE * 16.5 + HEAD),
    "header": (0, 0, TILE * (FIELD[0] + 5), HEAD),
    "header_text": (GAP, GAP),
    "exit_button": (TILE * (FIELD[0] + 5) - HEAD, 0, HEAD, HEAD),
    "keys_button": (TILE * (FIELD[0] + 5) - HEAD * 2 + GAP, 0, HEAD, HEAD),
    "keys_tooltip": (TILE * (FIELD[0] + 5) - HEAD * 2 + GAP, HEAD)
}

KEY_DELAYS = {
    "exit": (1000, 1000),
    "pause": (1000, 1000),
    "reset": (1000, 1000),
    "rotate cw": (200, 100),
    "rotate ccw": (200, 100),
    "rotate": (200, 100),
    "move left": (120, 20),
    "move right": (120, 20),
    "move down": (120, 20),
    "place": (200, 100),
}

pygame.font.init()
FONT = (
    pygame.font.Font(PATH["font"], int(TILE * 0.8)),
    pygame.font.Font(PATH["font"], int(TILE * 1.2)),
)

with open(PATH["datafile"], 'r') as FILE:
    DATA = json.load(FILE)

    COLORS = DATA["colors"]
    FIGURE_DATA = DATA["figures"]
    FIGURE_NAMES = tuple(FIGURE_DATA.keys())
    SOUND_DATA = DATA["sounds"]
