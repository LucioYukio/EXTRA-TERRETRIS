from mouse import Mouse
from screen import *

class Effect(Object):
    def __init__(self, image: str, total_frames: int, total_duration: int, width: int, height: int, tab: int, mouse: Mouse, h_parts: int = 8):
        super().__init__(image, width, height, tab, mouse, h_parts)
        self.set_total_frames(total_frames)
        self.frame_duration = total_duration/total_frames
        self.z = 2
    
    def update(self):
        super().update()
        if self._animation_time_elapsed >= self.frame_duration * self.total_frames:
            self.wants_to_die = True