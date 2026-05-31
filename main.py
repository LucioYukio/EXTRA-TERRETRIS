import csv
from random import randrange
import time

from screen import *
from button import *
from body import *
from nave import *
from enemy import *
from tetrisgrid import *
from text import Text
from tetris import Tetris

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

mouse   = Mouse()
teclado = k.Keyboard()

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
        inimigo = get_screen().add_object(EnemySin(
            img,
            int(DEFAULT_NAVE_SIZE.x),
            int(DEFAULT_NAVE_SIZE.y),
            tab,
            mouse,
            get_screen()._objs,
            teclado
        ))
    
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

# fps_text : Text = get_screen().add_object(Text(
#     TAB_JOGO, mouse
# ))
# fps_text.texts = ["FPS: ", 0]
# fps_text.color = "green"
# fps_text.y = TELA_H - fps_text.get_height()

# qtd_text : Text = get_screen().add_object(Text(
#     TAB_JOGO, mouse
# ))
# qtd_text.texts = ["Objetos: ", 0]
# qtd_text.color = "green"
# qtd_text.y = fps_text.y - qtd_text.get_height()

nave1 : Nave = get_screen().add_object(Nave(
    "assets/images/nave1.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    TAB_JOGO,
    get_screen().mouse,
    get_screen()._objs,
    teclado
 ))
nave1.x = get_screen().window.width/4 - nave1.get_width()/2
nave1.y = TELA_H - nave1.get_height() - 8
nave1.horizontal_bounds.y = get_screen().window.width/2
nave1.UP, nave1.DOWN, nave1.LEFT, nave1.RIGHT, nave1.SHOOT, nave1.POWER = control_esquemes[1]
nave1.z = 1
nave1.bullet_img = "assets/images/bullet_purple.png"
nave1.explosion_info["img"] = "assets/images/explosion_purple.png"
nave1.side = 0

nave2 : Nave = get_screen().add_object(Nave(
    "assets/images/nave2.png",
    int(DEFAULT_NAVE_SIZE.x),
    int(DEFAULT_NAVE_SIZE.y),
    TAB_JOGO,
    get_screen().mouse,
    get_screen()._objs,
    teclado
))
nave2.x = get_screen().window.width/4 + get_screen().window.width/2 - nave2.get_width()/2
nave2.y = get_screen().window.height - nave2.get_height() - 8
nave2.horizontal_bounds.x = get_screen().window.width/2
nave2.UP, nave2.DOWN, nave2.LEFT, nave2.RIGHT, nave2.SHOOT, nave2.POWER = control_esquemes[0]
nave2.z = 1
nave2.bullet_img = "assets/images/bullet_green.png"
nave2.explosion_info["img"] = "assets/images/explosion_green.png"
nave2.side = 1

# pontos1 : Text = get_screen().add_object(Text(
#     TAB_JOGO,
#     mouse
# ))
# pontos1.size = 32
# pontos1.texts = ["Pontos: ", 0]

# pontos2 : Text = get_screen().add_object(Text(
#     TAB_JOGO,
#     mouse
# ))
# pontos2.size = 32
# pontos2.texts = ["Pontos: ", 0]
# pontos2.x = TELA_W - pontos2.get_width()


TAB_TETRIS = 1

tetris : Tetris = get_screen().add_object(Tetris(
    Vector2(32,32),
    20,
    10,
    TAB_TETRIS,
    mouse,
    teclado
))

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
    # pontos1.texts[-1] = nave1.health
    
    get_screen().update()
    
    # qtd_text.texts[-1] = len(get_screen()._objs)
    
    intervalo = time.perf_counter() - tempo
    if intervalo < MAX_TEMPO_PASSADO:
        ticks += 1
        fps = ticks/intervalo
        # fps_text.texts[-1] = int(fps)
    else:
        # save in a file for profiling
        performance_log.append([len(get_screen()._objs), ticks/intervalo])
        if LOG_PERFORMANCE and teclado.key_pressed("l"):
            with open("performance.csv", "w") as file:
                w = csv.writer(file)
                w.writerow(["quantidade de objs", "fps"])
                w.writerows(performance_log)
        tempo = time.perf_counter()
        ticks = 0
        last_average_fps = fps
    

    