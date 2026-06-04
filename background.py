from typing import List

from screen import *

class Background(Object):
    """
    Background com 3 tiles verticais.
    Meio eh inteiro, borda esquerda ou direita sera dividida
    dependendo do argumento side (0 -> esquerdo tesselado; 1 -> direito tesselado).
    h_parts sera aplicada para cada borda.
    """
    def __init__(self, image: str, width: int, height: int, tabs: List[int], side: int, h_parts: int, anchor: Object, h_bounds: Vector2, add_to_screen: bool = True):
        super().__init__(EMPTY_PIXEL, width, height, tabs, 1, add_to_screen)
        
        self.keep_in_bounds = False
        self.horizontal_bounds = h_bounds
        self.vertical_bounds = Vector2(-1000,1000)
        self.anchor = anchor
        
        self.parts : List[Object] = []
        for i in range(3):
            parts = h_parts if (i == (1-side)*2) else 1
            self.parts.append(Object(image, width//3, height, tabs, parts))
            self.parts[-1].set_total_frames(3)
            self.parts[-1].playing = False
            self.parts[-1].set_curr_frame(i)
            self.parts[-1].horizontal_bounds = h_bounds
            self.parts[-1].categorie = f"background_part{i}"
            self.parts[-1].keep_in_bounds = False
        
        self.categorie = "background"
        
    
    def update(self):
        super().update()
        
        w = self.get_width()
        for i in range(3):
            self.parts[i].pos.x = self.pos.x + w*i/3
            self.parts[i].pos.y = self.pos.y