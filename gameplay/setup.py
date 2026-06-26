from copy import copy
from random import randrange
from typing import Any, Dict, List, Tuple

from config import tabs
from config.preload import preload_images
from engine.const import REF_RES
from engine.object import Object
from engine.screen import get_screen
from engine.vector2 import Vector2
from entities.asteroid import Asteroid
from entities.background import Background
from entities.nave import DEFAULT_NAVE_SIZE, Nave
from entities.powerstack import PowerStack
from entities.powerstores import NavePowerStore, TetrisPowerStore
from entities.winlosescreens import LoseScreen, WinScreen
from tetris.tetris import Tetris
from ui.persondisplay import GreenAlienDisplay, PurpleAlienDisplay
from ui.text import CompositeText, NumberText, Text

from .config import (
    BG_SCALE,
    CONTROL_SCHEMES,
    DIVISOR_W,
    H_BOUNDS,
    SIDEPANEL_W,
    SMALL_LETTER_SIZE,
    TETRIS_COLUMNS,
    TETRIS_LINES,
    ASTEROID_BASE_POINT_VALUE,
    ASTEROID_HEALTH_MULTIPLIER,
    DEFAULT_LETTER_SIZE,
)


def setup_tab_backgrounds():
    screen = get_screen()
    screen.bg_imgs[tabs.NAVE] = "assets/images/double_bg.png"
    screen.bg_imgs[tabs.TETRIS] = "assets/images/black_pixel.png"
    screen.bg_imgs[tabs.NAVE_LOJA] = "assets/images/white_circuit_background.png"
    screen.bg_imgs[tabs.TETRIS_LOJA] = "assets/images/white_circuit_background.png"


def setup_naves() -> Tuple[Nave, Nave]:
    nave1: Nave = Nave(
        "assets/images/nave1.png",
        int(DEFAULT_NAVE_SIZE.x),
        int(DEFAULT_NAVE_SIZE.y),
        0,
        [tabs.NAVE],
    )
    nave1.pos.x = REF_RES[0] / 4 - nave1.get_width() / 2
    nave1.pos.y = REF_RES[1] - nave1.get_height() - 8
    nave1.horizontal_bounds = copy(H_BOUNDS[0])
    nave1.UP, nave1.DOWN, nave1.LEFT, nave1.RIGHT, nave1.SHOOT, nave1.POWER = CONTROL_SCHEMES[1]
    nave1.bullet_img = "assets/images/bullet_purple.png"
    nave1.bullet_explosion_img = "assets/images/explosion_small_purple.png"
    nave1.side = 0

    nave2: Nave = Nave(
        "assets/images/nave2.png",
        int(DEFAULT_NAVE_SIZE.x),
        int(DEFAULT_NAVE_SIZE.y),
        1,
        [tabs.NAVE],
    )
    nave2.pos.x = REF_RES[0] / 4 + REF_RES[0] / 2 - nave2.get_width() / 2
    nave2.pos.y = REF_RES[1] - nave2.get_height() - 8
    nave2.horizontal_bounds = copy(H_BOUNDS[1])
    nave2.UP, nave2.DOWN, nave2.LEFT, nave2.RIGHT, nave2.SHOOT, nave2.POWER = CONTROL_SCHEMES[0]
    nave2.bullet_img = "assets/images/bullet_green.png"
    nave2.bullet_explosion_img = "assets/images/explosion_small_green.png"
    nave2.side = 1

    return nave1, nave2


def setup_backgrounds(naves: Tuple[Nave, Nave]) -> Tuple[List[Background], List[Background]]:
    bgs_far: List[Background] = []
    bgs: List[Background] = []

    bg_w = int(528 * BG_SCALE)
    bg_w -= bg_w % 96  # must be divisible by 96 (3 parts × 32 h_parts)

    for side in (0, 1):
        anchor = naves[side]
        x_start = H_BOUNDS[side].x if side == 0 else REF_RES[0] // 2
        x_end = REF_RES[0] // 2  if side == 0 else REF_RES[0]

        bg_far = Background(
            "assets/images/asteroids_bg_narrow.png",
            bg_w,
            int(2041 * BG_SCALE),
            [tabs.NAVE],
            side,
            32,
            anchor,
            Vector2(x_start, x_end),
        )
        bg_far.offset_multiplier = 0.1
        if side == 1:
            bg_far.pos.y = REF_RES[1] - bg_far.get_height() + 200
        bg_far.pos.x = x_start
        bgs_far.append(bg_far)

        bg = Background(
            "assets/images/asteroids_bg_narrow_close.png",
            bg_w,
            int(2041 * 3 * BG_SCALE),
            [tabs.NAVE],
            side,
            32,
            anchor,
            Vector2(x_start, x_end),
        )
        bg.offset_multiplier = 0.25
        bg.pos.y = REF_RES[1] - bg.get_height() if side == 0 else REF_RES[1] - bg.get_height() + 200
        bg.pos.x = x_start + 180*side
        bgs.append(bg)

    return bgs_far, bgs


def setup_asteroids(naves: Tuple[Nave, Nave], difficulty_mult: float,
                     auras: List[int]) -> List[Asteroid]:
    def get_random_pos(side: int):
        if side == 0:
            return randrange(0, REF_RES[0] // 2)
        else:
            return randrange(REF_RES[0] // 2, REF_RES[0])

    def spawn_asteroid(x: float, size: int, health: float, side: int):
        asteroid = Asteroid(size, size, side, health, [tabs.NAVE])
        asteroid.side = side
        asteroid.horizontal_bounds = copy(H_BOUNDS[side])
        asteroid.pos.x = x
        asteroid.pos.y = 0
        asteroid.anchor = naves[side]
        asteroid.speed = 200 * difficulty_mult
        return asteroid

    asteroids: List[Asteroid] = [
        spawn_asteroid(get_random_pos(0), 100, 1 * ASTEROID_HEALTH_MULTIPLIER, 0),
        spawn_asteroid(get_random_pos(0), 140, 2 * ASTEROID_HEALTH_MULTIPLIER, 0),
        spawn_asteroid(get_random_pos(0), 240, 3 * ASTEROID_HEALTH_MULTIPLIER, 0),
        spawn_asteroid(get_random_pos(1), 100, 1 * ASTEROID_HEALTH_MULTIPLIER, 1),
        spawn_asteroid(get_random_pos(1), 140, 2 * ASTEROID_HEALTH_MULTIPLIER, 1),
        spawn_asteroid(get_random_pos(1), 240, 3 * ASTEROID_HEALTH_MULTIPLIER, 1),
    ]

    i = 0
    total = len(asteroids) // 2
    for asteroid in asteroids:
        asteroid.pos.y = -(REF_RES[1] * (i + 1)) * 2
        asteroid.speed = 150 * (total - i + 1) / total
        asteroid.damage = i
        asteroid.points_list = auras
        asteroid.points_value = int(ASTEROID_BASE_POINT_VALUE * (i + 1))
        i = (i + 1) % total

    return asteroids


def setup_tetris(piece_size: Vector2) -> Tuple[Tetris, Tetris]:
    from .config import CONTROL_SCHEMES, TETRIS_LINES, TETRIS_COLUMNS
    tetris1: Tetris = Tetris(piece_size, TETRIS_LINES, TETRIS_COLUMNS, [tabs.TETRIS])
    tetris1.UP, tetris1.DOWN, tetris1.LEFT, tetris1.RIGHT, tetris1.SPIN, tetris1.POWER = CONTROL_SCHEMES[1]

    tetris2: Tetris = Tetris(piece_size, TETRIS_LINES, TETRIS_COLUMNS, [tabs.TETRIS])
    tetris2.UP, tetris2.DOWN, tetris2.LEFT, tetris2.RIGHT, tetris2.SPIN, tetris2.POWER = CONTROL_SCHEMES[0]
    tetris2.grid.FILLED = "assets/images/tile_filled_green.png"
    tetris2.grid.MARKED = "assets/images/tile_marked_green.png"
    tetris2.grid.overlay_img = "assets/images/tech_background_green_animated.png"
    tetris2.grid.build_grids()

    return tetris1, tetris2


def setup_power_stacks(tetris: Tuple[Tetris, Tetris], naves: Tuple[Nave, Nave]):
    tetris_power_stacks: List[PowerStack] = []
    nave_power_stacks: List[PowerStack] = []

    for side in (0, 1):
        tp = PowerStack(
            Vector2(64, 64), 6, 18, [tabs.TETRIS, tabs.TETRIS_LOJA], z=5,
            image="assets/images/powers_tetris.png",
        )
        tp.values = tetris[side].powers
        tp.pos.x = SIDEPANEL_W / 2 - tp.get_width() / 2 if side == 0 else REF_RES[0] - SIDEPANEL_W / 2 - tp.get_width() / 2
        tp.pos.y = 176
        tetris_power_stacks.append(tp)

        np = PowerStack(Vector2(64, 64), 6, 18, [tabs.NAVE, tabs.NAVE_LOJA], z=5)
        np.values = naves[side].powers
        np.pos.x = SIDEPANEL_W / 2 - np.get_width() / 2 if side == 0 else REF_RES[0] - SIDEPANEL_W / 2 - np.get_width() / 2
        np.pos.y = 176
        nave_power_stacks.append(np)

    return tetris_power_stacks, nave_power_stacks


def setup_stores(naves: Tuple[Nave, Nave], tetris: Tuple[Tetris, Tetris],
                 auras: List[int]) -> Tuple[NavePowerStore, TetrisPowerStore]:
    nave_store: NavePowerStore = NavePowerStore(
        [naves[0].powers, naves[1].powers], auras,
        [tabs.NAVE_LOJA], [CONTROL_SCHEMES[1], CONTROL_SCHEMES[0]],
    )

    tetris_store: TetrisPowerStore = TetrisPowerStore(
        [tetris[0].powers, tetris[1].powers], auras,
        [tabs.TETRIS_LOJA], [CONTROL_SCHEMES[1], CONTROL_SCHEMES[0]],
    )

    return nave_store, tetris_store


def setup_ui_elements(naves: Tuple[Nave, Nave]):
    aura_text: CompositeText = CompositeText(
        DEFAULT_LETTER_SIZE,
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA],
        color_index=1, background=True,
    )
    aura1_text_value = aura_text.add_number(4)
    aura_text.add_text(" ")
    aura2_text_value = aura_text.add_number(4)

    divisao = Object("assets/images/divisor.png", DIVISOR_W, REF_RES[1], [tabs.NAVE, tabs.TETRIS], z=3)
    divisao.pos.x = REF_RES[0] / 2 - divisao.get_width() / 2

    sidepanels: List[Object] = [
        Object(
            "assets/images/sidepanel_background_purple.png", SIDEPANEL_W, REF_RES[1],
            [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], z=3,
        ),
        Object(
            "assets/images/sidepanel_background_green.png", SIDEPANEL_W, REF_RES[1],
            [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], z=3,
        ),
    ]
    sidepanels[0].categorie = "sidepanel"
    sidepanels[1].pos.x = REF_RES[0] - sidepanels[1].get_width()

    points_texts: List[NumberText] = [
        NumberText(1, Vector2(SIDEPANEL_W, SIDEPANEL_W),
                   [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], 1, True),
        NumberText(1, Vector2(SIDEPANEL_W, SIDEPANEL_W),
                   [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], 1, True),
    ]
    points_texts[1].pos.x = REF_RES[0] - SIDEPANEL_W

    not_ready_texts: List[Text] = [
        Text("Comprando...", SMALL_LETTER_SIZE, [tabs.NAVE_LOJA, tabs.TETRIS_LOJA], 1, True),
        Text("Comprando...", SMALL_LETTER_SIZE, [tabs.NAVE_LOJA, tabs.TETRIS_LOJA], 1, True)
    ]
    not_ready_texts[0].keep_in_bounds = False
    not_ready_texts[1].keep_in_bounds = False
    
    ready_texts: List[Text] = [
        Text("Pronto.", SMALL_LETTER_SIZE, [tabs.NAVE_LOJA, tabs.TETRIS_LOJA], 1, True),
        Text("Pronto.", SMALL_LETTER_SIZE, [tabs.NAVE_LOJA, tabs.TETRIS_LOJA], 1, True)
    ]
    ready_texts[0].keep_in_bounds = False
    ready_texts[1].keep_in_bounds = False

    alien_displays: List = [
        PurpleAlienDisplay(120, int(120 * 1.25),
                           [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA],
                           lambda: (naves[0].health, naves[0].default_health)),
        GreenAlienDisplay(120, int(120 * 1.25),
                          [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA],
                          lambda: (naves[1].health, naves[1].default_health)),
    ]
    alien_displays[0].pos.x = sidepanels[0].get_center().x - alien_displays[0].get_width() / 2
    alien_displays[0].pos.y = REF_RES[1] - alien_displays[0].get_height()
    alien_displays[1].pos.x = sidepanels[1].get_center().x - alien_displays[1].get_width() / 2
    alien_displays[1].pos.y = REF_RES[1] - alien_displays[1].get_height()

    lose_screens: List[LoseScreen] = [
        LoseScreen(
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
            [tabs.NAVE, tabs.TETRIS],
        ),
        LoseScreen(
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
            [tabs.NAVE, tabs.TETRIS],
        ),
    ]
    lose_screens[0].pos.x = SIDEPANEL_W
    lose_screens[1].pos.x = int(REF_RES[0] / 2 + DIVISOR_W / 2)

    win_screens: List[WinScreen] = [
        WinScreen(
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
            [tabs.NAVE, tabs.TETRIS],
        ),
        WinScreen(
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
            [tabs.NAVE, tabs.TETRIS],
        ),
    ]
    win_screens[0].pos.x = SIDEPANEL_W
    win_screens[1].pos.x = int(REF_RES[0] / 2 + DIVISOR_W / 2)

    return (sidepanels, points_texts, aura_text,
            [aura1_text_value, aura2_text_value],
            alien_displays, lose_screens, win_screens, divisao,
            ready_texts, not_ready_texts)
