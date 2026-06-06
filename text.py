from screen import Object, List, Vector2, EMPTY_PIXEL, get_screen, get_text_size

SYMBOL_QUANTITY = 95
SYMBOL_OFFSET = 32

def int_to_ascii(x: int):
    return chr(x)

def ascii_to_int(c: str):
    return ord(c)

class Letter(Object):
    def __init__(self, letter: str, width: int, height: int, tabs: List[int], color_index : int = 0, background: bool = False):
        """
        color_index:
            black = 0
            white = 1
        """
        super().__init__("assets/images/letters_black_and_white.png", width, height, tabs, z=6)
        # (95 simbolos) * (quantidade de cores)
        self.set_total_frames(95 * 2)
        self.keep_in_bounds = False
        
        self.show_background : bool = background
        self._letter : str = ""
        self.letter_code : int = 0
        # Esse objeto esta mais preparado para preto e branco apenas, pelo menos por enquanto
        self.color_index : int = color_index # black= 0, white= 1
        
        
        self.background : Object = Object("assets/images/black_and_white_pixel.png", width, height, tabs, z=5)
        self.background.set_total_frames(2)
        self.background.playing = False
        
        self.playing = False
        
        self.set_letter(letter)
    
    def set_height(self, height: float):
        super().set_height(height)
        if hasattr(self, "background"):
            self.background.set_height(height)
    
    def set_width(self, width: float):
        super().set_width(width)
        if hasattr(self, "background"):
            self.background.set_width(width)
    
    def set_letter(self, letter: str):
        self._letter = letter
        self.letter_code = ascii_to_int(letter)

    def get_letter(self):
        return self._letter

    def increment_letter_code(self, amount: int):
        old_code = self.letter_code
        new_code = ((old_code - SYMBOL_OFFSET + amount) % SYMBOL_QUANTITY) + SYMBOL_OFFSET
        self.set_letter(chr(new_code))
    
    def update_curr_frame(self): # atualiza o curr_frame de acordo com self.letter e self.color_index
        self.sprites[0].set_curr_frame(
            (self.letter_code - 32) + # letra comecando do espaco
            (95 * self.color_index) # offset de acordo com a cor
        )
        
        self.background.sprites[0].set_curr_frame(1-self.color_index)

    def render(self):
        self.background.visible = self.show_background
        self.background.render()
        super().render()

    def update(self):
        super().update()
        self.background.pos.x = self.pos.x
        self.background.pos.y = self.pos.y
        
        self.update_curr_frame()
    
    def destroy(self):
        super().destroy()
        self.background.wants_to_die = True
        
class Text(Object):
    def __init__(self, text: str, letter_size: Vector2, tabs: List[int], color_index : int = 0, background: bool = False, newline_size: float = 0):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        
        self.text : str = text
        self.letter_size : Vector2 = letter_size
        self.newline_size : float = newline_size
        
        self.color_index : int = color_index
        self.background : bool = background
        
        self.letters : List[Letter] = []
        
        self.playing = False
        
        self.build_text()
        
    def build_text(self):
        w, h = int(self.letter_size.x), int(self.letter_size.y)
        
        for letter in self.letters:
            letter.wants_to_die = True
        self.letters.clear()
        
        for char in self.text:
            if char != '\n':
                letter : Letter = Letter(
                    char, w, h,
                    self.get_tabs(),
                    self.color_index, 
                    self.background)
                self.letters.append(letter)
    
    def set_color_index(self, color_index: int):
        self.color_index = color_index
        for l in self.letters:
            l.color_index = color_index
    
    def get_width(self):
        if not hasattr(self, "letters") or not self.letters:
            return 0
        self.apply_letter_position()
        farthest_letter = self.letters[0]
        for letter in self.letters:
            if letter.pos.x + letter.get_width() > farthest_letter.pos.x + farthest_letter.get_width():
                farthest_letter = letter
        return int(farthest_letter.pos.x + farthest_letter.get_width() - self.pos.x)


    def get_height(self):
        if not hasattr(self, "letters") or not self.letters:
            return 0
        self.apply_letter_position()
        return int(self.letters[-1].pos.y - self.pos.y + self.letters[-1].get_height())
    
    def apply_letter_position(self):
        w, h = int(self.letter_size.x), int(self.letter_size.y)
        line : int = 0
        column : int = 0
        
        i : int = 0 # char
        n_chars : int = len(self.text)
        j : int = 0 # letter
        n_letters : int = len(self.letters)
        while j < n_letters:
            char : str = " "
            if i < n_chars:
                char = self.text[i]
            letter : Letter = self.letters[j]
            
            if char != '\n':
                letter.pos.x = self.pos.x + (w * column)
                letter.pos.y = self.pos.y + (h + self.newline_size) * line
                j += 1
                column += 1
            else:
                column = 0
                line += 1
            i += 1
    def apply_coords(self, offset_x: float, offset_y: float):
        super().apply_coords(offset_x, offset_y)
        self.apply_letter_position()
        
    
    def destroy(self):
        super().destroy()
        for l in self.letters:
            l.wants_to_die = True

class NumberText(Text):
    def __init__(self, digits: int, letter_size: Vector2, tabs: List[int], color_index: int = 0, background: bool = False):
        self.digits = digits
        self.value : float = 0
        super().__init__("", letter_size, tabs, color_index, background)
        self.playing = False
        
    def set_digits(self, digits: int):
        self.digits = digits
        self.build_text()
    
    def build_text(self):
        w, h = int(self.letter_size.x), int(self.letter_size.y)
        
        for letter in self.letters:
            letter.wants_to_die = True
        self.letters.clear()
        
        self.letters = [Letter("0", w, h, self.get_tabs(), self.color_index, self.background) for _ in range(self.digits)]

    def update(self):
        super().update()
        self.text = str(int(self.value))
        digits_left = self.digits - len(self.text)
        if digits_left > 0:
            self.text = "0" * digits_left + self.text
        i : int = 0
        for digit in self.text:
            if i < self.digits:
                self.letters[i].set_letter(digit)
                i += 1

class TextField(Text):
    def __init__(self, digits: int, letter_size: Vector2, tabs: List[int], color_index: int = 0):
        self.digits = digits
        self.active_char: int = 0
        
        self.setinha_cima : Object = Object("assets/images/setinha_up.png", 16, 8, tabs, add_to_screen=False)
        self.setinha_baixo : Object = Object("assets/images/setinha_down.png", 16, 8, tabs, add_to_screen=False)

        self.LEFT = "left"
        self.RIGHT = "right"
        self.UP = "up"
        self.DOWN = "down"

        self.input_interval : float = 0.15
        self.input_cooldown : float = 0

        super().__init__("A"*digits, letter_size, tabs, color_index, background=True)

    def load_text(self, text: str):
        i = 0
        for c in text:
            if i > self.digits:
                break
            self.letters[i].set_letter(c)
    
    def parse_text(self):
        txt : str = ""
        for letter in self.letters:
            txt = "".join([txt, letter.get_letter()])
        return txt

    def update_appearance(self):
        for i in range(self.digits):
            if self.active_char != i:
                self.letters[i].color_index = self.color_index
            else:
                self.letters[i].color_index = self.color_index
                self.setinha_cima.pos.x = self.letters[i].get_center().x - self.setinha_cima.get_width()/2
                self.setinha_cima.pos.y = self.letters[i].pos.y - self.setinha_cima.get_height() - 6
                self.setinha_cima.apply_coords(0,0)
                
                self.setinha_baixo.pos.x = self.setinha_cima.pos.x
                self.setinha_baixo.pos.y = self.letters[i].pos.y + self.get_height() + 6
                self.setinha_baixo.apply_coords(0,0)

    def walk_active_char(self, amount: int = 1):
        self.active_char = (self.active_char + amount) % self.digits

    def render(self):
        super().render()
        self.setinha_cima.render()
        self.setinha_baixo.render()

    def change_char(self, char: int, amount: int = 1):
        self.letters[char].increment_letter_code(amount)

    def update(self):
        side_step = self._keyboard.key_pressed(self.RIGHT) - self._keyboard.key_pressed(self.LEFT)
        vertical_step = self._keyboard.key_pressed(self.UP) - self._keyboard.key_pressed(self.DOWN)

        if self.input_cooldown <= 0 and (side_step != 0 or vertical_step != 0):
            self.walk_active_char(side_step)
            self.change_char(self.active_char, vertical_step)
            self.input_cooldown = self.input_interval
        else:
            self.input_cooldown -= self.delta_time

        self.update_appearance()
        super().update()


class CompositeText(Object):
    def __init__(self, letter_size: Vector2, tabs: List[int], color_index: int = 0, background: bool = False, newline_size: float = 0):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        self.playing = False
        
        self.texts : List[Text] = []
        self.letter_size : Vector2 = letter_size
        self.color_index : int = color_index
        self.background : bool = background
        self.newline_size : float = newline_size

    def apply_text_position(self):
        last_coord: Vector2 = Vector2(self.pos.x, self.pos.y)
        for text in self.texts:
            text.pos.x = last_coord.x
            text.pos.y = last_coord.y
            last_coord = Vector2(
                text.pos.x + text.get_width(),
                text.pos.y
            )
            if text.text and text.text[-1] == '\n':
                last_coord.y += text.letter_size.y + self.newline_size
                last_coord.x = self.pos.x

    def apply_coords(self, offset_x: float, offset_y: float):
        super().apply_coords(offset_x, offset_y)
        self.apply_text_position()
            
    def add_text(self, text: str):
        self.texts.append(Text(text, self.letter_size, self.get_tabs(), self.color_index, self.background, self.newline_size))
        
    def add_number(self, digits: int):
        number_text = NumberText(digits, self.letter_size, self.get_tabs(), self.color_index, self.background)
        self.texts.append(number_text)
        return number_text

    def add_field(self, digits: int, color_index: int = -1):
        if color_index == -1:
            color_index = self.color_index
        textfield = TextField(digits, self.letter_size, self.get_tabs(), color_index)
        self.texts.append(textfield)
        return textfield

    def clear(self):
        for text in self.texts:
            text.wants_to_die = True

    def get_width(self):
        if not hasattr(self, "texts") or not self.texts:
            return 0
        self.apply_text_position()
        farthest_point : float = 0
        for text in self.texts:
            point = text.pos.x + text.get_width()
            if point > farthest_point:
                farthest_point = point
        return int(farthest_point - self.pos.x)

    def get_height(self):
        if not hasattr(self, "texts") or not self.texts:
            return 0
        self.apply_text_position()
        return int(self.texts[-1].pos.y + self.texts[-1].get_height() - self.pos.y)
        
    
class DrawnText(Object):
    """USES DRAWTEXT"""
    texts : List = []
    size : int = 12
    color = "white"
    font_name : str = "Arial"
    def __init__(self, tabs: List[int]):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs, z=4)
        # serao desenhados em sequencia na tela
        self.texts : List = []
        self.categorie = "UI"
    
    def get_text(self):
        return "".join([str(txt) for txt in self.texts])
    
    def render(self):
        get_screen().window.draw_text(self.get_text(), self.pos.x, self.pos.y, self.size, self.color, self.font_name)
    
    def get_text_size(self):
        return get_text_size(self.get_text(), self.font_name, self.size)
    
    def get_height(self):
        return self.get_text_size()[1]
    
    def get_width(self):
        return self.get_text_size()[0]
    