# botoes onde voce pode modificar o texto e o tamanho vai de acordo.
# botao tem dois sprites, um preto e um branco,
# o preto encobre o preto e o branco eh um pouco maior e fica atras.
# normalmente o branco nao aparece, so quando o mouse passa por cima.
# quando clicado, o texto fica preto e o sprite preto fica invisivel.
# tem uma variavel de estado que diz se esta sendo clicado ou nao, mas
# so eh acessivel por funcao

import types

from screen import *
from pplay.animation import Animation
import pygame.transform

BLACK_PIXEL : str = "assets/images/black_pixel.png"
WHITE_PIXEL : str = "assets/images/white_pixel.png"

class Button(Object):
    def __init__(self, text: str, size: int, tab: int, mouse: Mouse, x : int = 0, y : int = 0):
        """Tela da qual o objeto pertence"""
        self._tab = tab
        
        """Coordenadas locais em relacao ao centro"""
        self.x : float = 0
        self.y : float = 0
        
        self.visible : bool     = True
        self.enabled : bool = True
        self.keep_in_bounds : bool = False
        
        """Variaveis dos botoes"""
        self.black_sprite : Animation = Animation(BLACK_PIXEL, 1)
        self.white_sprite : Animation = Animation(WHITE_PIXEL, 1)
        self._margin_x : int = 5
        self._margin_y : int = 3
        self._border_width : int = 3
        
        """Variaveis do texto"""
        self._text : str = text
        self._size : int = size
        self._font : str = "Courier New"
        self._color_normal = "white"
        self._color_pressed = "black"
        
        """Variaveis do Object"""
        self._mouse : Mouse = mouse
        self.categorie = "UI"
        
        self.update_sprite()
        
    def get_text(self):
        return self._text
    
    def set_text(self, text : str):
        self._text = text
        self.update_sprite()
    
    def get_size(self):
        return self._size
    
    def set_size(self, size: int):
        self._size = size
        self.update_sprite()
    
    def get_color_normal(self):
        return self._color_normal
    
    def set_color_normal(self, color):
        self._color_normal = color
        self.update_sprite()
    
    def get_color_pressed(self):
        return self._color_pressed
    
    def set_color_pressed(self, color):
        self._color_pressed = color
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
        return get_text_size(self._text, self._font, self._size)
    
    def is_hovered(self):
        return self._mouse.is_over_object(self.black_sprite) or self._mouse.is_over_object(self.white_sprite) and self.enabled
    
    def update_sprite(self):
        """Mudar o tamanho das imagens de acordo com o texto
        e atribuir novos sprites as variaveis."""

        txt_w, txt_h = self.get_text_size()
        
        self.black_sprite.image = pygame.transform.scale(
            self.black_sprite.image, 
            (txt_w + self._margin_x * 2, txt_h + self._margin_y * 2)
            )
        self.black_sprite.width, self.black_sprite.height = self.black_sprite.image.get_size()
        
        self.white_sprite.image = pygame.transform.scale(
            self.white_sprite.image, 
            (txt_w + self._margin_x * 2 + self._border_width * 2, txt_h + self._margin_y * 2 + self._border_width * 2)
            )
        self.white_sprite.width, self.white_sprite.height = self.white_sprite.image.get_size()
    
    def apply_coords(self, offset_x: float, offset_y: float):
        txt_w, txt_h = self.get_text_size()
        self.black_sprite.x = self.x + offset_x
        self.black_sprite.y = self.y + offset_y
        self.white_sprite.x = self.black_sprite.x - self._border_width
        self.white_sprite.y = self.black_sprite.y - self._border_width
            
    def render(self):
        color = self._color_normal
        
        if self.is_pressed():
            color = self._color_pressed
            self.white_sprite.draw()
        elif self.is_hovered():
            self.white_sprite.draw()
            self.black_sprite.draw()
        else:
            self.black_sprite.draw()
        
        get_screen().window.draw_text(
            self._text, 
            self.x + self._margin_x, 
            self.y + self._margin_y,
            self._size,
            color,
            self._font,
            )