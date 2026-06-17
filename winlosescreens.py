from typing import List

from fades import BlackFadeOut
from screen import Object, res_scale

class StatusScreen(Object):
    """Tela que mostra se o jogador perdeu ou ganhou no fim do round"""
    def __init__(self, image: str, width: int, height: int, tabs: List[int]):
        super().__init__(image, width, height, tabs, 1, True, 5)
        self.set_total_frames(2)
        
        self.show_timer : float = 0
    
    def show(self, seconds: float):
        """mostra essa tela por algum tempo"""
        self.show_timer = seconds
    
    def update(self):
        super().update()
        
        if self.show_timer > 0:
            self.show_timer -= self.delta_time
            self.visible = True
            if self.show_timer <= 0:
                # fade out
                fade = BlackFadeOut(self.get_tabs(), 1, int(self.get_width()*res_scale[0]), int(self.get_height()*res_scale[1]))
                fade.pos = self.pos
        else:
            self.visible = False

class LoseScreen(StatusScreen):
    def __init__(self, width: int, height: int, tabs: List[int]):
        super().__init__("assets/images/lose_screen.png", width, height, tabs)

class WinScreen(StatusScreen):
    def __init__(self, width: int, height: int, tabs: List[int]):
        super().__init__("assets/images/win_screen.png", width, height, tabs)