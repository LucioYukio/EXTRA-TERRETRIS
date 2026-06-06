# botoes onde voce pode modificar o texto e o tamanho vai de acordo.
# botao tem dois sprites, um preto e um branco,
# o preto encobre o preto e o branco eh um pouco maior e fica atras.
# normalmente o branco nao aparece, so quando o mouse passa por cima.
# quando clicado, o texto fica preto e o sprite preto fica invisivel.
# tem uma variavel de estado que diz se esta sendo clicado ou nao, mas
# so eh acessivel por funcao

from screen import Object, Vector2, List, Mouse, get_screen, EMPTY_PIXEL
from text import Text

BLACK_PIXEL : str = "assets/images/black_pixel.png"
WHITE_PIXEL : str = "assets/images/white_pixel.png"

class Button(Object):
    def __init__(self, text: str, letter_size: Vector2, tabs: List[int]):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs)
        self._tab = tabs
        self.z = 4
 
        self.keep_in_bounds : bool = False
        
        """Variaveis do texto"""
        self.letter_size : Vector2 = letter_size
        self.text : Text = Text(text, letter_size, tabs)
        
        """Variaveis dos botoes"""
        self.white_sprite : Object = Object(WHITE_PIXEL, 1, 1, tabs)
        self.white_sprite.z = 3
        self.black_sprite : Object = Object(BLACK_PIXEL, 1, 1, tabs)
        self.black_sprite.z = 3
        self._margin_x : int = 16
        self._margin_y : int = 8
        self._border_width : int = 3
        
        """Variaveis do Object"""
        self._mouse : Mouse = get_screen().mouse
        self.categorie = "UI"
        
        self.update_sprite()

    def get_border_width(self):
        return self._border_width
    
    def set_border_width(self, width: int):
        self._border_width = width
        self.update_sprite()
        
    def get_margin(self):
        return (self._margin_x, self._margin_y)
    
    def set_margin(self, margin_x, margin_y):
        self._margin_x = margin_x
        self._margin_y = margin_y
        self.update_sprite()
    
    def get_text_size(self):
        return Vector2(self.text.get_width(), self.text.get_height())
    
    def get_width(self):
        if hasattr(self, "white_sprite"):
            return self.white_sprite.get_width()
        return 0
    
    def get_height(self):
        if hasattr(self, "white_sprite"):
            return self.white_sprite.get_height()
        return 0
    
    def update_sprite(self):
        """Mudar o tamanho das imagens de acordo com o texto
        e atribuir novos sprites as variaveis."""

        txt_s = self.get_text_size()
        
        self.black_sprite.set_width(txt_s.x + self._margin_x * 2)
        self.black_sprite.set_height(txt_s.y + self._margin_y * 2)
        
        self.white_sprite.set_width(txt_s.x + self._margin_x * 2 + self._border_width * 2)
        self.white_sprite.set_height(txt_s.y + self._margin_y * 2 + self._border_width * 2)
        # print("black_sprite width:",  self.black_sprite.get_width())
        # print("black_sprite height:", self.black_sprite.get_height())
        # print("white_sprite width:",  self.white_sprite.get_width())
        # print("white_sprite height:", self.white_sprite.get_height())
            
    def update(self):
        super().update()
        self.black_sprite.pos.x = self.pos.x
        self.black_sprite.pos.y = self.pos.y
        self.white_sprite.pos.x = self.black_sprite.pos.x - self._border_width
        self.white_sprite.pos.y = self.black_sprite.pos.y - self._border_width
        self.text.pos.x = self.black_sprite.pos.x + self._margin_x
        self.text.pos.y = self.black_sprite.pos.y + self._margin_y  
         
        self.update_sprite()
        
        self.white_sprite.visible = self.is_hovered()
        self.black_sprite.visible =  not self.is_pressed()
        self.text.set_color_index(not self.is_pressed())