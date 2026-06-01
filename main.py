import csv
from random import randrange
import time

from screen import *
from button import *
from body import *
from nave import *
from enemy import *
from text import *
from tetris import *

LOG_PERFORMANCE = True
performance_log : List[List[float]] = []
## se o fps for menor que isso, tomar algumas medidas, como nao spawnar novos inimigos
## apenas uma medida preventiva, o fps pode acabar sendo menos que o target.
FPS_TARGET: float = 60
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

enemy_spawn_interval : float = 0.2
enemy_spawn_cooldown : float = 0
MAX_ENEMY_COUNT : int = 50 *2
enemy_horizontal_padding : int = 8 # padding to account for when spawning enemies

#---------------- FUNCOES ---------------------------

def get_random_pos(side: int):
    if side == 0: # esquerda
        return randrange(enemy_horizontal_padding, int(get_screen().window.width/2))
    else:
        return randrange(int(get_screen().window.width/2) + enemy_horizontal_padding, int(get_screen().window.width) - enemy_horizontal_padding)

def reset_enemy(enemy: Enemy):
    enemy.x = get_random_pos(enemy.side)
    enemy.y = -enemy.get_height() + 1
    enemy.health = enemy.default_health

def spawn_enemy(x: float, tab: int, horizontal_bounds : Tuple[int, int], side: int, inimigo: Enemy | None = None):
    img : str = "assets/images/nave_inimiga_verde.png" if side == 0 else "assets/images/nave_inimiga_roxa.png"
    if not isinstance(inimigo, Enemy):
        inimigo = EnemySin(
            img,
            int(DEFAULT_NAVE_SIZE.x),
            int(DEFAULT_NAVE_SIZE.y),
            tab,
            get_screen()._objs
        )
    
    if isinstance(inimigo, Enemy):
        x = clamp(x, 0, get_screen().window.width - inimigo.get_width())
        inimigo.x = x
        inimigo.y = -inimigo.get_height() + 1
        inimigo.horizontal_bounds = Vector2(horizontal_bounds[0], horizontal_bounds[1])
        inimigo.vertical_bounds = Vector2(-inimigo.get_height(), get_screen().window.height + inimigo.get_height())
        inimigo.bullet_img = "assets/images/bullet_green.png" if side == 0  else "assets/images/bullet_purple.png"
        inimigo.explosion_info["img"] = "assets/images/explosion_green.png" if side == 0 else "assets/images/explosion_purple.png"
        inimigo.side = side

def enemy_count():
    count : int = 0
    for obj in get_screen()._objs:
        if isinstance(obj, Enemy):
            count += 1
    return count

#---------------- TABS -----------------

TAB_JOGO = 0

get_screen().bg_imgs[TAB_JOGO] = "assets/images/double_bg.png"

nave1 : Nave = Nave(
    "assets/images/nave1.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    TAB_JOGO,
    get_screen()._objs,
 )
nave1.x = get_screen().window.width/4 - nave1.get_width()/2
nave1.y = TELA_H - nave1.get_height() - 8
nave1.horizontal_bounds.y = get_screen().window.width/2
nave1.UP, nave1.DOWN, nave1.LEFT, nave1.RIGHT, nave1.SHOOT, nave1.POWER = control_esquemes[1]
nave1.z = 1
nave1.bullet_img = "assets/images/bullet_purple.png"
nave1.explosion_info["img"] = "assets/images/explosion_purple.png"
nave1.side = 0

nave2 : Nave = Nave(
    "assets/images/nave2.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    TAB_JOGO,
    get_screen()._objs
)
nave2.x = get_screen().window.width/4 + get_screen().window.width/2 - nave2.get_width()/2
nave2.y = get_screen().window.height - nave2.get_height() - 8
nave2.horizontal_bounds.x = get_screen().window.width/2
nave2.UP, nave2.DOWN, nave2.LEFT, nave2.RIGHT, nave2.SHOOT, nave2.POWER = control_esquemes[0]
nave2.z = 1
nave2.bullet_img = "assets/images/bullet_green.png"
nave2.explosion_info["img"] = "assets/images/explosion_green.png"
nave2.side = 1


TAB_TETRIS = 1

tetris : Tetris = Tetris(
    Vector2(32,32),
    20,
    10,
    TAB_TETRIS,
)

fps_text : CompositeText = CompositeText(
    Vector2(32,32), # tamanho do texto
    TAB_TETRIS, # tab
    color_index=0, 
    background=True
)
fps_text.add_text("FPS:")
fps_text_value : NumberText = fps_text.add_number(4)

gooner_text : CompositeText = CompositeText(
    Vector2(32,32), 
    TAB_TETRIS, 
    color_index=1, 
    background=False)
gooner_text.add_text("Gooner...")

gooner_text.y = 64

# -----------

# ------------------------- Game Loop ----------------------------

# quando a diferenca do perf counter do frame for maior do q MAX,
# tempo = tempo do frame e ticks = 0
MAX_TEMPO_PASSADO = 2
ticks = 0
tempo = time.perf_counter()

get_screen().set_tab(1)
while True:
    #----------------------- Callback Dos Botoes ----------------------
    # --------
    
    if get_screen().get_tab == TAB_JOGO:
        #----------------------- Enemy Spawn ------------------------------
        if enemy_spawn_cooldown <= 0 and enemy_count() + 2 <= MAX_ENEMY_COUNT and last_average_fps > FPS_TARGET:
            spawn_enemy(get_random_pos(0), TAB_JOGO, (-100, int(get_screen().window.width/2)), 0)
            spawn_enemy(get_random_pos(1), TAB_JOGO, (int(get_screen().window.width/2), int(get_screen().window.width) + 100), 1)
            enemy_spawn_cooldown = enemy_spawn_interval
        
        for o in get_screen()._objs:
            if o.y >= TELA_H and isinstance(o, Enemy):
                reset_enemy(o)
    # --------
    
    # drain cooldowns
    enemy_spawn_cooldown = max(enemy_spawn_cooldown - get_screen().window.delta_time(), 0)
    
    # update UI
    
    
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
    

    