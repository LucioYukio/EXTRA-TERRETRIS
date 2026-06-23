import csv
from copy import copy
from random import randrange
import time

from button import Button
import tabs
from asteroid import Asteroid
from background import Background
from enemy import Enemy, EnemySin
from nave import DEFAULT_NAVE_SIZE, Nave
from persondisplay import GreenAlienDisplay, PurpleAlienDisplay
from screen import (List, Vector2, TELA_W, TELA_H, REF_RES, clamp,
                    get_screen, Object, update_res_scale)
from tetris import Tetris
from text import CompositeText, Text
import gameplay

#------------------------- CONSTANTES ---------------------------------------------------------

update_res_scale([TELA_W, TELA_H])
get_screen().set_title("Extraterretris")

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

DEFAULT_LETTER_SIZE = Vector2(32,32)
SMALL_LETTER_SIZE = Vector2(16,16)

#--------------------------------------------------------------------------------------------

# Menu principal

start_button : Button = Button("Jogar", DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL])

#-----

# Tela de Loading

loading_text : Text = Text("Carregando...", DEFAULT_LETTER_SIZE, [tabs.LOADING], 1)

get_screen().set_tab(tabs.MENU_PRINCIPAL)
while True:
    match get_screen().get_tab():
        case tabs.MENU_PRINCIPAL:
            if start_button.is_just_pressed():
                # ir para tela de loading
                # carregar jogo
                get_screen().set_tab(tabs.LOADING)
        case tabs.LOADING:
            print("na tab de loading")
            get_screen().clear_tab(tabs.NAVE)
            get_screen().clear_tab(tabs.TETRIS)
            gameplay.play_game()
            get_screen().set_tab(tabs.MENU_PRINCIPAL)
    get_screen().update()