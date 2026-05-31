from pplay.animation import Animation
from screen import *
from screen import Mouse

class Text(Object):
    texts : List = []
    size : int = 12
    color = "white"
    font_name : str = "Arial"
    def __init__(self, tab: int, mouse: Mouse):
        super().__init__("assets/images/empty_pixel.png", 0, 0, tab, mouse)
        # serao desenhados em sequencia na tela
        self.texts : List = []
        self.z = 3
        self.categorie = "UI"
    
    def get_text(self):
        return "".join([str(txt) for txt in self.texts])
    
    def render(self, window: w.Window):
        window.draw_text(self.get_text(), self.x, self.y, self.size, self.color, self.font_name)
    
    def get_text_size(self):
        return get_text_size(self.get_text(), self.font_name, self.size)
    
    def get_height(self):
        return self.get_text_size()[1]
    
    def get_width(self):
        return self.get_text_size()[0]
    