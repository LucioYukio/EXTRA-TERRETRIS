from screen import *

class Effect(Object):
    def __init__(self, image: str, total_frames: int, total_duration: int, width: int, height: int, tabs: List[int], h_parts: int = 8):
        super().__init__(image, width, height, tabs, h_parts)
        self.set_total_frames(total_frames)
        self.frame_duration = total_duration/total_frames
        self.z = 2
    
    def update_sprites(self, grow_a_bit: bool = True, h_mult: int = 1):
        grow_a_bit = False
        super().update_sprites(grow_a_bit, h_mult)
    
    def update(self):
        super().update()
        if self.time_elapsed >= self.frame_duration * self.total_frames:
            self.wants_to_die = True