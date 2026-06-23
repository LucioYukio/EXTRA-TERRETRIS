from typing import List

from engine.const import EMPTY_PIXEL
from engine.object import Object
from engine.vector2 import Vector2

IMAGE = "assets/images/powers_nave.png"
TOTAL_FRAMES = 10


class PowerStack(Object):
    def __init__(self, icon_size: Vector2, n_icons: int, gap: int, tabs: List[int], z: int = 0,
                 image: str = IMAGE, total_frames: int = TOTAL_FRAMES):
        width = int(icon_size.x)
        height = int(n_icons * icon_size.y + (n_icons - 1) * gap)
        super().__init__(EMPTY_PIXEL, width, height, tabs, 1, z=z)

        self.playing = False
        self.icon_size = icon_size
        self.n_icons = n_icons
        self.gap = gap
        self.total_frames = total_frames
        self.values: List[int] = []
        self.icons: List[Object] = []

        for _ in range(n_icons):
            icon = Object(image, int(icon_size.x), int(icon_size.y), tabs, 1, z=z + 1)
            icon.set_total_frames(total_frames)
            icon.playing = False
            icon.visible = False
            self.icons.append(icon)

    def set_values(self, values: List[int]):
        self.values = values.copy()

    def update(self):
        super().update()
        for i, icon in enumerate(self.icons):
            icon.pos.x = self.pos.x
            icon.pos.y = self.pos.y + i * (self.icon_size.y + self.gap)

            idx_from_bottom = self.n_icons - 1 - i
            if idx_from_bottom < len(self.values):
                icon.visible = True
                icon.set_curr_frame(self.values[idx_from_bottom])
            else:
                icon.visible = False

    def destroy(self):
        super().destroy()
        for icon in self.icons:
            icon.wants_to_die = True
