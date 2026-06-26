from typing import List
from engine.const import REF_RES
from engine.vector2 import Vector2
from entities.enemy import Enemy, EnemySin, SpinEnemy

SIDEPANEL_W = 120
DIVISOR_W = 48

H_BOUNDS: List[Vector2] = [
    Vector2(SIDEPANEL_W, REF_RES[0] / 2 - DIVISOR_W / 2),
    Vector2(REF_RES[0] / 2 + DIVISOR_W / 2, REF_RES[0] - SIDEPANEL_W),
]

CONTROL_SCHEMES: List[List[str]] = [
    ["up", "down", "left", "right", "n", "m"],
    ["w", "s", "a", "d", "space", "left_shift"],
]

ENEMY_POOL =    ["Enemy" for _ in     range(40)] +\
                ["EnemySin" for _ in  range(40)] +\
                ["SpinEnemy" for _ in range(20)]

DIFFICULTY_MULT = {"lento": 0.5, "normal": 1, "rapido": 10}

TETRIS_LINES = 20
TETRIS_COLUMNS = 10

DEFAULT_LETTER_SIZE = Vector2(32, 32)
SMALL_LETTER_SIZE = Vector2(16, 16)

BG_VELOCITY = 0.2
BG_SCALE = 1.66

ASTEROID_RESET_INTERVAL = 5
ASTEROID_HEALTH_MULTIPLIER = 10
ASTEROID_BASE_POINT_VALUE = 30

TETRIS_POINTS_MULTIPLIER = 5
AURA_REWARD_MULTIPLIER = 10

NAVE_SPEED_INCREASE = 2
ENEMY_SPEED_DECREASE = 0.75
SHIELD_UP_DURATION = 5
TETRIS_GRAVITY_INCREASE = 2
TETRIS_GRAVITY_DECREASE = 0.5

MAX_ENEMY_COUNT = 20
MAX_ENEMY_BULLET_COUNT = 60
