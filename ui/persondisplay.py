from typing import List, Callable

from ui.button import BLACK_PIXEL
from engine.screen import Object, Vector2

class PersonDisplay(Object):
    """
    Imagem do Alien que fica com raiva quando leva dano.
    Sprite do objeto em si eh o alien em idle, e esse objeto
    tem um outro objeto que eh o Sprite com raiva, que fica invisivel
    normalmente, mas que fica visivel quando esta com raiva.
    """
    def __init__(self, idle_image: str, total_idle_frames: int, angry_image: str, total_angry_frames: int, width: int, height: int, tabs: List[int], health_getter: Callable[[], tuple[int, int]]):
        super().__init__(idle_image, width, height, tabs, z = 4)
        self.set_total_frames(total_idle_frames)
        
        self.angry_sprite : Object = Object(angry_image, width, height, tabs, z = self.z)
        self.angry_sprite.set_total_frames(total_angry_frames)
        
        self.angry_duration : float = 1
        self.angry_timer : float = 0
    
        self.background : Object = Object("assets/images/black_to_red.png", width, height, tabs, z = self.z-1)
        self.background.set_total_frames(128)
        self.background.playing = False
        self.health_getter = health_getter
    
    def hurt(self):
        self.angry_timer = self.angry_duration
    
    def update(self):
        super().update()
        
        self.angry_sprite.pos = self.pos
        self.background.pos = self.pos

        health, default_health = self.health_getter()
        if health > default_health:
            self.background.set_curr_frame(0)
        else:
            ratio = max(0, health / default_health) if default_health > 0 else 0
            frame = 127 - int(ratio * 127)
            self.background.set_curr_frame(frame)
        
        if self.angry_timer > 0:
            self.visible = False
            self.angry_sprite.visible = True
            self.angry_timer -= self.delta_time
        else:
            self.visible = True
            self.angry_sprite.visible = False

class GreenAlienDisplay(PersonDisplay):
    # 120 x 150, 1.25 factor
    def __init__(self, width: int, height: int, tabs: List[int], health_getter):
        super().__init__("assets/images/alien_green_idle.png", 67, "assets/images/alien_green_angry.png", 43, width, height, tabs, health_getter)
        self.frame_duration = 0.05
        self.angry_sprite.frame_duration = 0.002
    
class PurpleAlienDisplay(PersonDisplay):
    # 120 x 150, 1.25 factor
    def __init__(self, width: int, height: int, tabs: List[int], health_getter):
        super().__init__("assets/images/alien_purple_idle.png", 40, "assets/images/alien_purple_angry.png", 79, width, height, tabs, health_getter)
        self.frame_duration = 0.05
        self.angry_sprite.frame_duration = 0.001
