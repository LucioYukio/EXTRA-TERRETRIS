import os
import sys
from typing import List


if getattr(sys, 'frozen', False):
    import pygame
    _orig_load = pygame.image.load
    def _patched_load(filename, *args, **kwargs):
        if not os.path.isabs(filename):
            filename = os.path.join(sys._MEIPASS, filename)
        return _orig_load(filename, *args, **kwargs)
    pygame.image.load = _patched_load


def resolve_asset_path(path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, path)
    return path


REF_RES = (1600, 900)
res_scale: List[float] = [1, 1]

TELA_W = 1920
TELA_H = 1080

def resize_window(w: int, h: int):
    global TELA_W, TELA_H
    TELA_W = w
    TELA_H = h
    update_res_scale([w, h])
    get_screen().resize(w, h)

EMPTY_PIXEL = "assets/images/empty_pixel.png"

screen_instance = None


def update_res_scale(new_res: List[float]):
    global REF_RES, res_scale
    res_scale[0] = new_res[0] / REF_RES[0]
    res_scale[1] = new_res[1] / REF_RES[1]


def clamp(x, min_val, max_val):
    if x < min_val:
        return min_val
    if x > max_val:
        return max_val
    return x


def pt_to_px(pt: float):
    return pt * 1.333


def get_text_size(text: str, font_name: str, size_pt: int):
    import pygame.font
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.SysFont(font_name, size_pt)
    return font.size(text)


def get_screen():
    global screen_instance
    if screen_instance is None:
        from engine.screen import Screen
        screen_instance = Screen(TELA_W, TELA_H)
    return screen_instance
