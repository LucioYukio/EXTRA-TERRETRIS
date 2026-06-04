from pplay.animation import Animation
from screen import *
from screen import Vector2

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
        super().__init__("assets/images/letters_black_and_white.png", width, height, tabs)
        # (95 simbolos) * (quantidade de cores)
        self.set_total_frames(95 * 2)
        self.z = 6
        self.keep_in_bounds = False
        
        self.show_background : bool = background
        self._letter : str = ""
        self.letter_code : int = 0
        # Esse objeto esta mais preparado para preto e branco apenas, pelo menos por enquanto
        self.color_index : int = color_index # black= 0, white= 1
        
        
        self.background : Object = Object("assets/images/black_and_white_pixel.png", width, height, tabs)
        self.background.set_total_frames(2)
        self.background.playing = False
        
        self.background.z = 5
        
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
        self.letter_code = ascii_to_int(letter)
    
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
    def __init__(self, text: str, letter_size: Vector2, tabs: List[int], color_index : int = 0, background: bool = False):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        
        self.text : str = text
        self.letter_size : Vector2 = letter_size
        
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
                letter.pos.y = self.pos.y + (h * line)
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

class CompositeText(Object):
    def __init__(self, letter_size: Vector2, tabs: List[int], color_index: int = 0, background: bool = False):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        self.playing = False
        
        self.texts : List[Text] = []
        self.letter_size : Vector2 = letter_size
        self.color_index : int = color_index
        self.background : bool = background
    
    def apply_coords(self, offset_x: float, offset_y: float):
        super().apply_coords(offset_x, offset_y)
        
        last_coord : Vector2 = Vector2(self.pos.x, self.pos.y)
        for text in self.texts:
            text.pos.x = last_coord.x
            text.pos.y = last_coord.y
            text.apply_coords(offset_x, offset_y)
            last_coord = Vector2(
                text.letters[-1].pos.x + text.letter_size.x,
                text.letters[-1].pos.y
            )
            
    def add_text(self, text: str):
        """Add a static Text object to this Composite Text"""
        self.texts.append(Text(text, self.letter_size, self.get_tabs(), self.color_index, self.background))
        
    def add_number(self, digits: int):
        number_text = NumberText(digits, self.letter_size, self.get_tabs(), self.color_index, self.background)
        self.texts.append(number_text)
        return number_text

    def get_width(self):
        if not hasattr(self, "texts") or not self.texts:
            return 0
        farthest_point : float = 0
        for text in self.texts:
            point = text.pos.x + text.get_width()
            if point > farthest_point:
                farthest_point = point
        return int(farthest_point - self.pos.x)

    def get_height(self):
        if not hasattr(self, "texts") or not self.texts:
            return 0
        return int(self.texts[-1].pos.y + self.texts[-1].get_height() - self.pos.y)
        
    
class DrawnText(Object):
    """USES DRAWTEXT"""
    texts : List = []
    size : int = 12
    color = "white"
    font_name : str = "Arial"
    def __init__(self, tabs: List[int]):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        # serao desenhados em sequencia na tela
        self.texts : List = []
        self.z = 4
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
    