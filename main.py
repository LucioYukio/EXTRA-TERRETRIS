from button import Button
import sounds
import tabs
from screen import (List, Vector2, TELA_W, TELA_H, REF_RES,
                    get_screen, update_res_scale)
from text import Text
import gameplay

#------------------------- CONSTANTES ---------------------------------------------------------

update_res_scale([TELA_W, TELA_H])
get_screen().set_title("Extraterretris")

DEFAULT_LETTER_SIZE = Vector2(32,32)

#--------------------------------------------------------------------------------------------

# Menu principal

difficulty_names = ["lento", "normal", "frenetico"]
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
            # position and update difficulty buttons
            label_text = "Dificuldade: " + difficulty_names[selected_difficulty]
            if difficulty_label.text != label_text:
                difficulty_label.text = label_text
                difficulty_label.build_text()
            difficulty_label.pos.x = TELA_W/2 - difficulty_label.get_width()/2
            difficulty_label.pos.y = TELA_H/2 - 135

            for i, btn in enumerate(difficulty_buttons):
                btn.pos.y = TELA_H/2 - 70 + i * 48
                btn.pos.x = TELA_W/2 - btn.get_width()/2
                if btn.is_just_pressed():
                    selected_difficulty = i
                btn.text.set_color_index(1 if i == selected_difficulty else 0)

            # position and update points buttons
            pts_label_text = "Pontos: " + str(points_values[selected_points])
            if points_label.text != pts_label_text:
                points_label.text = pts_label_text
                points_label.build_text()
            points_label.pos.x = TELA_W/2 - points_label.get_width()/2
            points_label.pos.y = difficulty_buttons[-1].pos.y + difficulty_buttons[-1].get_height() + 20

            for i, btn in enumerate(points_buttons):
                btn.pos.y = points_label.pos.y + points_label.get_height() + 5 + i * 48
                btn.pos.x = TELA_W/2 - btn.get_width()/2
                if btn.is_just_pressed():
                    selected_points = i
                btn.text.set_color_index(1 if i == selected_points else 0)

            start_button.pos.y = points_buttons[-1].pos.y + points_buttons[-1].get_height() + 30
            start_button.pos.x = TELA_W/2 - start_button.get_width()/2

            if start_button.is_just_pressed():
                get_screen().set_tab(tabs.LOADING)
        case tabs.LOADING:
            print("na tab de loading")
            get_screen().clear_tab(tabs.NAVE)
            get_screen().clear_tab(tabs.TETRIS)
            gameplay.play_game(difficulty_names[selected_difficulty], points_values[selected_points])
            get_screen().set_tab(tabs.MENU_PRINCIPAL)
    get_screen().update()