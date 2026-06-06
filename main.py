import csv
from copy import copy
from random import randrange
import time

from asteroid import Asteroid
from background import Background
from enemy import Enemy, EnemySin
from nave import DEFAULT_NAVE_SIZE, Nave
from screen import (List, Vector2, TELA_W, TELA_H, REF_RES, clamp,
                    get_screen, Object, update_res_scale)
from tetris import Tetris
from text import CompositeText


#------------------------- CONSTANTES ---------------------------------------------------------

LOG_PERFORMANCE = True
performance_log : List[List[float]] = []
## se o fps for menor que isso, tomar algumas medidas, como nao spawnar novos inimigos
## apenas uma medida preventiva, o fps pode acabar sendo menos que o target.
FPS_TARGET: float = 0
fps : float = 0
last_average_fps : float = 9999

update_res_scale([TELA_W, TELA_H])
screen = get_screen()
screen.set_title("Extraterretris")

# variaveis de botao
botoes_gap  = 20
botoes_size = 45

DIF_FACIL   = 0.5
DIF_MEDIO   = 1
DIF_DIFICIL = 2
dificuldade = DIF_MEDIO

# cima, baixo, esquerda, direita, tiro, poder
control_esquemes = [
    ["up", "down", "left", "right", "n", "m"], 
    ["w", "s", "a", "d", "space", "alt"]
]

enemy_spawn_interval : float = 2.2 # cuidado! nao botar o mesmo que o intervalo de tiro.
enemy_spawn_cooldown : float = 0
MAX_ENEMY_COUNT : int = 100 *2
MAX_ENEMY_BULLET_COUNT : int = 10 *2

TETRIS_LINES = 20
TETRIS_COLUMNS = 10

DEFAULT_LETTER_SIZE = Vector2(32,32)
SMALL_LETTER_SIZE = Vector2(16,16)

SIDEPANEL_W = 120
DIVISOR_W = 48

H_BOUNDS = [Vector2(SIDEPANEL_W, TELA_W/2 - DIVISOR_W/2), Vector2(TELA_W/2 + DIVISOR_W/2, TELA_W-SIDEPANEL_W)]

# velocity in which the background descends
BG_VELOCITY = 0.2
BG_SCALE = 1.66

ASTEROID_RESET_INTERVAL : float = 5 # intervalo para esse asteroid voltar la pra cima depois de sair da tela
ASTEROID_HEALTH_MULTIPLIER : float = 10
ASTEROID_BASE_POINT_VALUE : float = 30

auras : List[int] = [0, 0]

# counters
# Eh uma lista para eu poder linkar em inimigos eh poder decrementar na morte
enemy_counter        : List[int] = [0] 
enemy_bullet_counter : List[int] = [0]
asteroid_counter     : List[int] = [0]

#-------------------------------------------------------------------




#---------------- FUNCOES ---------------------------

def get_random_pos(side: int):
    if side == 0: # esquerda
        return randrange(0, TELA_W//2)
    else:
        return randrange(TELA_W//2, TELA_W)

def reset_enemy(enemy: Enemy):
    enemy.pos.x = get_random_pos(enemy.side)
    enemy.pos.y = -enemy.get_height() + 1
    enemy.health = enemy.default_health

def spawn_enemy(x: float, tabs: List[int], side: int, inimigo: Enemy | None = None):
    img : str = "assets/images/nave_inimiga_verde.png" if side == 0 else "assets/images/nave_inimiga_roxa.png"
    if not isinstance(inimigo, Enemy):
        inimigo = EnemySin(
            img,
            int(DEFAULT_NAVE_SIZE.x),
            int(DEFAULT_NAVE_SIZE.y),
            nave1 if side == 0 else nave2,
            tabs
        )
        inimigo.instance_counter = enemy_counter
        inimigo.bullet_instance_counter = enemy_bullet_counter
        inimigo.max_bullet_count = MAX_ENEMY_BULLET_COUNT
        
    if isinstance(inimigo, Enemy):
        x = clamp(x, 0, get_screen().window.width - inimigo.get_width())
        inimigo.pos.x = x
        inimigo.pos.y = -inimigo.get_height() + 1
        inimigo.horizontal_bounds = copy(H_BOUNDS[side])
        if side == 0:
            inimigo.anchor = nave1
        else:
            inimigo.anchor = nave2
        inimigo.vertical_bounds = Vector2(-inimigo.get_height(), get_screen().window.height + inimigo.get_height())
        inimigo.bullet_img = "assets/images/bullet_green.png" if side == 0  else "assets/images/bullet_purple.png"
        inimigo.bullet_explosion_img = "assets/images/explosion_small_green.png" if side == 0  else "assets/images/explosion_small_purple.png"
        inimigo.side = side
        inimigo.points_list = auras

def spawn_asteroid(x: float, size: int, health: float, tabs: List[int], side: int):
    asteroid = Asteroid(size, size, health, tabs)
    asteroid.side = side
    asteroid.horizontal_bounds = copy(H_BOUNDS[side])
    asteroid.pos.x = x
    asteroid.pos.y = 0
    if side == 0:
        asteroid.anchor = nave1
        asteroid.horizontal_bounds.x
    else:
        asteroid.anchor = nave2
        asteroid.horizontal_bounds.y
    return asteroid
    

# def enemy_count():
#     count : int = 0
#     for obj in get_screen()._objs:
#         if isinstance(obj, Enemy):
#             count += 1
#     return count

#---------------- TABS -----------------

TAB_JOGO = 0

get_screen().bg_imgs[TAB_JOGO] = "assets/images/double_bg.png"



nave1 : Nave = Nave(
    "assets/images/nave1.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    [TAB_JOGO],
)
nave1.pos.x = get_screen().window.width/4 - nave1.get_width()/2
nave1.pos.y = TELA_H - nave1.get_height() - 8
nave1.horizontal_bounds = copy(H_BOUNDS[0])
nave1.UP, nave1.DOWN, nave1.LEFT, nave1.RIGHT, nave1.SHOOT, nave1.POWER = control_esquemes[1]
nave1.z = 1
nave1.bullet_img = "assets/images/bullet_purple.png"
nave1.bullet_explosion_img = "assets/images/explosion_small_purple.png"
nave1.side = 0

nave2 : Nave = Nave(
    "assets/images/nave2.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    [TAB_JOGO],
)
nave2.pos.x = get_screen().window.width/4 + get_screen().window.width/2 - nave2.get_width()/2
nave2.pos.y = get_screen().window.height - nave2.get_height() - 8
nave2.horizontal_bounds = H_BOUNDS[1]
nave2.UP, nave2.DOWN, nave2.LEFT, nave2.RIGHT, nave2.SHOOT, nave2.POWER = control_esquemes[0]
nave2.z = 1
nave2.bullet_img = "assets/images/bullet_green.png"
nave2.bullet_explosion_img = "assets/images/explosion_small_green.png"

nave2.side = 1

asteroid_bg1 : Background = Background(
    "assets/images/asteroids_bg_narrow.png",
    int(528 * BG_SCALE),
    int(2041 * BG_SCALE),
    [TAB_JOGO],
    0,
    32,
    nave1,
    Vector2(SIDEPANEL_W, TELA_W/2 - 16)
)
asteroid_bg1.offset_multiplier = 0.2
asteroid_bg1.pos.y = TELA_H - asteroid_bg1.get_height()
asteroid_bg1.pos.x = 30

asteroid_bg2 : Background = Background(
    "assets/images/asteroids_bg_narrow.png",
    int(528 * BG_SCALE),
    int(2041 * BG_SCALE),
    [TAB_JOGO],
    1,
    32,
    nave2,
    Vector2(TELA_W/2, TELA_W)
)
asteroid_bg2.offset_multiplier = 0.2
asteroid_bg2.pos.y = TELA_H - asteroid_bg2.get_height() + 200 # numero aleatorio para variar
asteroid_bg2.pos.x = TELA_W/2 - 100

asteroids : List[Asteroid] = [
    spawn_asteroid(get_random_pos(0), 100, 1 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 0),
    spawn_asteroid(get_random_pos(0), 140, 2 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 0),
    spawn_asteroid(get_random_pos(0), 240, 3 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 0),
    spawn_asteroid(get_random_pos(1), 100, 1 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 1),
    spawn_asteroid(get_random_pos(1), 140, 2 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 1),
    spawn_asteroid(get_random_pos(1), 240, 3 * ASTEROID_HEALTH_MULTIPLIER, [TAB_JOGO], 1),
]
i = 0
total = len(asteroids)//2
for asteroid in asteroids:
    asteroid.pos.y = -(TELA_H * (i + 1)) *2
    asteroid.speed = 150 * (total - i+1)/total
    asteroid.damage = i
    asteroid.points_list = auras
    asteroid.points_value = ASTEROID_BASE_POINT_VALUE * (i + 1)
    i = (i + 1) % total


fps_text = CompositeText(SMALL_LETTER_SIZE, [TAB_JOGO], color_index=1, background=True)
fps_text.add_text("FPS:")
fps_text_value = fps_text.add_number(3)


TAB_TETRIS = 1

piece_size = Vector2(REF_RES[1]/TETRIS_LINES, REF_RES[1]/TETRIS_LINES)

tetris1 : Tetris = Tetris(
    piece_size,
    TETRIS_LINES,
    TETRIS_COLUMNS,
    [TAB_TETRIS],
)
tetris1.UP, tetris1.DOWN, tetris1.LEFT, tetris1.RIGHT, tetris1.SPIN, tetris1.POWER = control_esquemes[1]

tetris2 : Tetris = Tetris(
    piece_size,
    TETRIS_LINES,
    TETRIS_COLUMNS,
    [TAB_TETRIS],
)
tetris2.UP, tetris2.DOWN, tetris2.LEFT, tetris2.RIGHT, tetris2.SPIN, tetris2.POWER = control_esquemes[0]
tetris2.grid.FILLED = "assets/images/tile_filled_green.png"
tetris2.grid.MARKED = "assets/images/tile_marked_green.png"
tetris2.grid.overlay_img = "assets/images/tech_background_green_animated.png"
tetris2.grid.build_grids()


# general
aura_text : CompositeText = CompositeText(DEFAULT_LETTER_SIZE, [TAB_JOGO, TAB_TETRIS], color_index=1, background=True)
aura1_text_value = aura_text.add_number(4)
aura_text.add_text(" ")
aura2_text_value = aura_text.add_number(4)

sidepanel1 : Object = Object("assets/images/sidepanel_background_purple.png", SIDEPANEL_W, 900, [TAB_JOGO, TAB_TETRIS])
sidepanel1.z = 3
sidepanel1.categorie = "sidepanel"

sidepanel2 : Object = Object("assets/images/sidepanel_background_green.png", SIDEPANEL_W, 900, [TAB_JOGO, TAB_TETRIS])
sidepanel2.z = 3
sidepanel2.pos.x = TELA_W - sidepanel2.get_width()

divisao = Object("assets/images/divisor.png", DIVISOR_W, REF_RES[1], [TAB_JOGO, TAB_TETRIS])
divisao.pos.x = TELA_W/2 - divisao.get_width()/2
divisao.z = 3

# -----------

# ------------------------- Game Loop ----------------------------

# quando a diferenca do perf counter do frame for maior do q MAX,
# tempo = tempo do frame e ticks = 0
MAX_TEMPO_PASSADO = 2
ticks = 0
tempo = time.perf_counter()

get_screen().set_tab(TAB_JOGO)
while True:
    #----------------------- Callback Dos Botoes ----------------------
    # --------
    
    if get_screen().get_tab() == TAB_JOGO:
        #----------------------- Enemy Spawn ------------------------------
        if enemy_spawn_cooldown <= 0 and enemy_counter[0] + 2 <= MAX_ENEMY_COUNT and last_average_fps > FPS_TARGET:
            spawn_enemy(get_random_pos(0), [TAB_JOGO], 0)
            spawn_enemy(get_random_pos(1), [TAB_JOGO], 1)
            enemy_spawn_cooldown = enemy_spawn_interval
        
        for o in get_screen()._objs:
            if o.pos.y >= TELA_H and isinstance(o, Enemy):
                reset_enemy(o)
        
        asteroid_bg1.pos.y += BG_VELOCITY
        if asteroid_bg1.pos.y >= -asteroid_bg1.get_height()/3:
            asteroid_bg1.pos.y -= asteroid_bg1.get_height()/3
        asteroid_bg2.pos.y += BG_VELOCITY
        if asteroid_bg2.pos.y >= -asteroid_bg2.get_height()/3:
            asteroid_bg2.pos.y -= asteroid_bg2.get_height()/3


        for asteroid in asteroids:
            if asteroid.pos.y >= TELA_H:
                asteroid.pos.y = TELA_H * 2 # (necessariamente fora da tela)
            if asteroid.reset_timer >= ASTEROID_RESET_INTERVAL:
                # reset asteroid
                asteroid.pos.y = -asteroid.get_height() 
                asteroid.pos.x = get_random_pos(asteroid.side)
        
        fps_text.pos.x = SIDEPANEL_W
        
    #-------------------------------------------------
    if get_screen().get_tab() == TAB_TETRIS:
        tetris1.pos.x = divisao.pos.x - tetris1.get_width()
        tetris2.pos.x = divisao.pos.x + divisao.get_width()
        
    # --------
    
    # drain cooldowns
    enemy_spawn_cooldown = max(enemy_spawn_cooldown - get_screen().window.delta_time(), 0)
    
    # update UI
    aura_text.pos.x = TELA_W/2 - aura_text.get_width()/2
    aura_text.pos.y = TELA_H - aura_text.get_height()
    aura1_text_value.value = auras[0]
    aura2_text_value.value = auras[1]

    get_screen().update()
    
    # qtd_text.texts[-1] = len(get_screen()._objs)
    
    intervalo = time.perf_counter() - tempo
    if intervalo < MAX_TEMPO_PASSADO:
        ticks += 1
        fps = ticks/intervalo
        fps_text_value.value = int(fps)
    else:
        # save in a file for profiling
        performance_log.append([len(get_screen()._objs), ticks/intervalo])
        if LOG_PERFORMANCE and get_screen().keyboard.key_pressed("l"):
            with open("performance.csv", "w") as file:
                w = csv.writer(file)
                w.writerow(["quantidade de objs", "fps"])
                w.writerows(performance_log)
        tempo = time.perf_counter()
        ticks = 0
        last_average_fps = fps


    