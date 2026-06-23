from typing import List

REF_RES = (1600, 900)
res_scale: List[float] = [1, 1]

TELA_W = 1600
TELA_H = 900

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
