from typing import List

from engine.object import Object


class Effect(Object):
    def __init__(self, image: str, total_frames: int, total_duration: float, width: int, height: int, tabs: List[int], h_parts: int = 2, z: int = 2):
        super().__init__(image, width, height, tabs, h_parts, z=z)
        self.set_total_frames(total_frames)
        self.frame_duration = total_duration / total_frames

        self.queue_for_destruction = False

    def update_sprites(self, grow_a_bit: bool = True):
        super().update_sprites(False)

    def update(self):
        super().update()
        if self.time_elapsed >= self.frame_duration * self.total_frames:
            self.wants_to_die = True

    def animate(self):
        if self.time_elapsed >= self.frame_duration * (self.total_frames - 1):
            self.wants_to_die = True
        super().animate()
