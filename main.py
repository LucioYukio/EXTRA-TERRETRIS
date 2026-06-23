from typing import List

from config import sounds
from config import tabs
from engine.const import TELA_W, TELA_H, REF_RES, get_screen, update_res_scale
from engine.object import Object
from engine.vector2 import Vector2
from ui.button import Button
from ui.text import Text
import gameplay

#------------------------- CONSTANTES ---------------------------------------------------------

update_res_scale([TELA_W, TELA_H])
get_screen().set_title("Extraterretris")

DEFAULT_LETTER_SIZE = Vector2(32,32)

#--------------------------------------------------------------------------------------------

# Menu principal

title : Object = Object("assets/images/title_card_white.png", REF_RES[0], REF_RES[1], [tabs.MENU_PRINCIPAL])

difficulty_names = ["lento", "normal", "ultra-sonico"]
difficulty_buttons : List[Button] = []
for name in difficulty_names:
    difficulty_buttons.append(Button(name, DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL]))

difficulty_label : Text = Text("", DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL], 1)

points_values = [3, 6, 9]
points_buttons : List[Button] = []
for v in points_values:
    points_buttons.append(Button(str(v), DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL]))

points_label : Text = Text("", DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL], 1)

start_button : Button = Button("Jogar", DEFAULT_LETTER_SIZE, [tabs.MENU_PRINCIPAL])
selected_difficulty : int = 1
selected_points : int = 0

#-----

# Tela de Loading

loading_text : Text = Text("Carregando...", DEFAULT_LETTER_SIZE, [tabs.LOADING], 1)

get_screen().set_tab(tabs.MENU_PRINCIPAL)
while True:
    if sounds.MUSICA.is_playing():
        sounds.MUSICA.stop()
    match get_screen().get_tab():
        case tabs.MENU_PRINCIPAL:
            center_x = [REF_RES[0] // 8, REF_RES[0] // 2 + 200, REF_RES[0] * 7 // 8]
            bottom_y = REF_RES[1] - 20

            # Difficulty group (anchored from bottom, growing up)
            difficulty_label.pos.x = center_x[0] - difficulty_label.get_width() // 2
            difficulty_label.pos.y = bottom_y - 194

            label_text = "Velocidade: " + difficulty_names[selected_difficulty]
            if difficulty_label.text != label_text:
                difficulty_label.text = label_text
                difficulty_label.build_text()

            for i, btn in enumerate(difficulty_buttons):
                btn.pos.x = center_x[0] - btn.get_width() // 2
                btn.pos.y = bottom_y - 140 + i * 48
                if btn.is_just_pressed():
                    selected_difficulty = i
                btn.text.set_color_index(1 if i == selected_difficulty else 0)

            # Rounds group (anchored from bottom, growing up)
            points_label.pos.x = center_x[1] - points_label.get_width() // 2
            points_label.pos.y = bottom_y - 194

            pts_label_text = "Pontos: " + str(points_values[selected_points])
            if points_label.text != pts_label_text:
                points_label.text = pts_label_text
                points_label.build_text()

            for i, btn in enumerate(points_buttons):
                btn.pos.x = center_x[1] - btn.get_width() // 2
                btn.pos.y = bottom_y - 140 + i * 48
                if btn.is_just_pressed():
                    selected_points = i
                btn.text.set_color_index(1 if i == selected_points else 0)

            # Start group
            start_button.pos.x = center_x[2] - start_button.get_width() // 2
            start_button.pos.y = bottom_y - 90

            if start_button.is_just_pressed():
                get_screen().set_tab(tabs.LOADING)
        case tabs.LOADING:
            loading_text.pos.x = REF_RES[0] // 2 - loading_text.get_width() // 2
            loading_text.pos.y = REF_RES[1] // 2 - loading_text.get_height() // 2
            print("na tab de loading")
            get_screen().clear_tab(tabs.NAVE)
            get_screen().clear_tab(tabs.NAVE_LOJA)
            get_screen().clear_tab(tabs.TETRIS)
            get_screen().clear_tab(tabs.TETRIS_LOJA)
            gameplay.play_game(difficulty_names[selected_difficulty], points_values[selected_points])
            get_screen().set_tab(tabs.MENU_PRINCIPAL)
    get_screen().update()