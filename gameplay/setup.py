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
from ui.text import CompositeText, NumberText

from .config import (
    BG_SCALE,
    CONTROL_SCHEMES,
    DIVISOR_W,
    H_BOUNDS,
    SIDEPANEL_W,
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


def setup_backgrounds(nave1: Nave, nave2: Nave) -> Tuple[Background, Background, Background, Background]:
    asteroid_bg_far1: Background = Background(
        "assets/images/asteroids_bg_narrow.png",
        int(528 * BG_SCALE),
        int(2041 * BG_SCALE),
        [tabs.NAVE],
        0,
        32,
        nave1,
        Vector2(SIDEPANEL_W, REF_RES[0] / 2 - 16),
    )
    asteroid_bg_far1.offset_multiplier = 0.1

    asteroid_bg1: Background = Background(
        "assets/images/asteroids_bg_narrow_close.png",
        int(528 * BG_SCALE),
        int(2041 * 3 * BG_SCALE),
        [tabs.NAVE],
        0,
        32,
        nave1,
        Vector2(SIDEPANEL_W, REF_RES[0] / 2 - 16),
    )
    asteroid_bg1.offset_multiplier = 0.25
    asteroid_bg1.pos.y = REF_RES[1] - asteroid_bg1.get_height()
    asteroid_bg1.pos.x = 60

    asteroid_bg_far2: Background = Background(
        "assets/images/asteroids_bg_narrow.png",
        int(528 * BG_SCALE),
        int(2041 * BG_SCALE),
        [tabs.NAVE],
        1,
        32,
        nave2,
        Vector2(REF_RES[0] / 2, REF_RES[0]),
    )
    asteroid_bg_far2.offset_multiplier = 0.1
    asteroid_bg_far2.pos.y = REF_RES[1] - asteroid_bg_far2.get_height() + 200
    asteroid_bg_far2.pos.x = REF_RES[0] / 2

    asteroid_bg2: Background = Background(
        "assets/images/asteroids_bg_narrow_close.png",
        int(528 * BG_SCALE),
        int(2041 * 3 * BG_SCALE),
        [tabs.NAVE],
        1,
        32,
        nave2,
        Vector2(REF_RES[0] / 2, REF_RES[0]),
    )
    asteroid_bg2.offset_multiplier = 0.25
    asteroid_bg2.pos.y = REF_RES[1] - asteroid_bg2.get_height() + 200
    asteroid_bg2.pos.x = REF_RES[0] / 2

    return asteroid_bg_far1, asteroid_bg1, asteroid_bg_far2, asteroid_bg2


def setup_asteroids(nave1: Nave, nave2: Nave, difficulty_mult: float,
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
        asteroid.anchor = nave1 if side == 0 else nave2
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


def setup_power_stacks(tetris1: Tetris, tetris2: Tetris, nave1: Nave, nave2: Nave):
    tetris_powers1: PowerStack = PowerStack(
        Vector2(64, 64), 6, 18, [tabs.TETRIS, tabs.TETRIS_LOJA], z=5,
        image="assets/images/powers_tetris.png",
    )
    tetris_powers1.values = tetris1.powers
    tetris_powers1.pos.x = SIDEPANEL_W / 2 - tetris_powers1.get_width() / 2
    tetris_powers1.pos.y = 176

    tetris_powers2: PowerStack = PowerStack(
        Vector2(64, 64), 6, 18, [tabs.TETRIS, tabs.TETRIS_LOJA], z=5,
        image="assets/images/powers_tetris.png",
    )
    tetris_powers2.values = tetris2.powers
    tetris_powers2.pos.x = REF_RES[0] - SIDEPANEL_W / 2 - tetris_powers2.get_width() / 2
    tetris_powers2.pos.y = 176

    nave_powers1: PowerStack = PowerStack(Vector2(64, 64), 6, 18, [tabs.NAVE, tabs.NAVE_LOJA], z=5)
    nave_powers1.values = nave1.powers
    nave_powers1.pos.x = SIDEPANEL_W / 2 - nave_powers1.get_width() / 2
    nave_powers1.pos.y = 176

    nave_powers2: PowerStack = PowerStack(Vector2(64, 64), 6, 18, [tabs.NAVE, tabs.NAVE_LOJA], z=5)
    nave_powers2.values = nave2.powers
    nave_powers2.pos.x = REF_RES[0] - SIDEPANEL_W / 2 - nave_powers2.get_width() / 2
    nave_powers2.pos.y = 176

    return tetris_powers1, tetris_powers2, nave_powers1, nave_powers2


def setup_stores(nave1: Nave, nave2: Nave, tetris1: Tetris, tetris2: Tetris,
                 auras: List[int]) -> Tuple[NavePowerStore, TetrisPowerStore]:
    nave_store: NavePowerStore = NavePowerStore(
        [nave1.powers, nave2.powers], auras,
        [tabs.NAVE_LOJA], [CONTROL_SCHEMES[1], CONTROL_SCHEMES[0]],
    )

    tetris_store: TetrisPowerStore = TetrisPowerStore(
        [tetris1.powers, tetris2.powers], auras,
        [tabs.TETRIS_LOJA], [CONTROL_SCHEMES[1], CONTROL_SCHEMES[0]],
    )

    return nave_store, tetris_store


def setup_ui_elements(nave1: Nave, nave2: Nave) -> Dict[str, Any]:
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

    sidepanel1: Object = Object(
        "assets/images/sidepanel_background_purple.png", SIDEPANEL_W, REF_RES[1],
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], z=3,
    )
    sidepanel1.categorie = "sidepanel"

    points_text1: NumberText = NumberText(
        1, Vector2(SIDEPANEL_W, SIDEPANEL_W),
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], 1, True,
    )

    purple_alien_display: PurpleAlienDisplay = PurpleAlienDisplay(
        120, int(120 * 1.25),
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA],
        lambda: (nave1.health, nave1.default_health),
    )
    purple_alien_display.pos.x = sidepanel1.get_center().x - purple_alien_display.get_width() / 2
    purple_alien_display.pos.y = REF_RES[1] - purple_alien_display.get_height()

    sidepanel2: Object = Object(
        "assets/images/sidepanel_background_green.png", SIDEPANEL_W, REF_RES[1],
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], z=3,
    )
    sidepanel2.pos.x = REF_RES[0] - sidepanel2.get_width()

    points_text2: NumberText = NumberText(
        1, Vector2(SIDEPANEL_W, SIDEPANEL_W),
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA], 1, True,
    )
    points_text2.pos.x = REF_RES[0] - SIDEPANEL_W

    green_alien_display: GreenAlienDisplay = GreenAlienDisplay(
        120, int(120 * 1.25),
        [tabs.NAVE, tabs.NAVE_LOJA, tabs.TETRIS, tabs.TETRIS_LOJA],
        lambda: (nave2.health, nave2.default_health),
    )
    green_alien_display.pos.x = sidepanel2.get_center().x - green_alien_display.get_width() / 2
    green_alien_display.pos.y = REF_RES[1] - green_alien_display.get_height()

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

    return {
        "sidepanel1": sidepanel1,
        "sidepanel2": sidepanel2,
        "points_text1": points_text1,
        "points_text2": points_text2,
        "aura_text": aura_text,
        "aura1_text_value": aura1_text_value,
        "aura2_text_value": aura2_text_value,
        "purple_alien_display": purple_alien_display,
        "green_alien_display": green_alien_display,
        "lose_screens": lose_screens,
        "win_screens": win_screens,
        "divisao": divisao,
    }
