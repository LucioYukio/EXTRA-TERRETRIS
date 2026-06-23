from typing import List

import pplay.keyboard as k
import pygame.transform
from engine.animation import Animation
from engine.const import REF_RES, res_scale, EMPTY_PIXEL, get_screen
from engine.imagecache import get_image
from engine.mouse import Mouse
from engine.vector2 import Vector2


class Object:
    _width: int = 0
    _height: int = 0
    horizontal_bounds: Vector2 = Vector2(-1, -1)
    vertical_bounds: Vector2 = Vector2(-1, -1)
    out_of_h_bounds: bool = False
    out_of_v_bounds: bool = False

    def __init__(self, image: str, width: int, height: int, tabs: List[int], h_parts: int = 1, add_to_screen: bool = True, z: int = 0):
        self._mouse = get_screen().mouse
        self._keyboard = get_screen().keyboard

        self.image = image
        self.sprites: List[Animation] = []
        self.h_parts = h_parts
        self._tabs = tabs
        self.pos = Vector2()
        self.last_pos = Vector2()
        self._z = z
        self.offset_multiplier = 0
        self.anchor = self
        self.frame_duration : float = 1
        self.total_frames = 1

        self.set_width(width)
        self.set_height(height)
        self.build_sprites()

        self.visible = True
        self.enabled = True
        self.playing = True
        self.delta_time = 0
        self.time_elapsed = 0
        self.out_of_screen = False
        self.horizontal_bounds = Vector2(-1, -1)
        self.vertical_bounds = Vector2(-1, -1)
        self.out_of_h_bounds = False
        self.out_of_v_bounds = False
        self.screen_size = Vector2(1600, 900)
        self.keep_in_bounds = True
        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = False
        self.categorie = ""
        self.tags = []
        self.instance_counter: List[int] = [0]
        self._id = 0
        self.wants_to_die = False
        self.dead = False
        self._initialized = False

        if add_to_screen:
            get_screen().add_object(self)
        self._initialized = True

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, value):
        if self._z != value:
            self._z = value
            if self._initialized:
                get_screen().order_objs_by_z()

    def get_tabs(self):
        return self._tabs

    def add_tab(self, tab: int):
        self._tabs.append(tab)

    def remove_tab(self, tab: int):
        self._tabs.remove(tab)

    def get_id(self):
        return self._id

    def set_id(self, id: int):
        self._id = id

    def get_width(self):
        return self._width / res_scale[0]

    def set_width(self, width: float):
        if self._width != width:
            self._width = int(width * res_scale[0])
            self.update_sprites()

    def get_height(self):
        return self._height / res_scale[1]

    def set_height(self, height: float):
        if self._height != height:
            self._height = int(height * res_scale[1])
            self.update_sprites()

    def set_total_frames(self, total_frames: int):
        self.total_frames = total_frames
        self.playing = True
        self.build_sprites()

    def get_center(self):
        return Vector2(self.pos.x + self.get_width() / 2, self.pos.y + self.get_height() / 2)

    def build_sprites(self):
        self.sprites.clear()
        for i in range(self.h_parts):
            spr = Animation(self.image, self.total_frames)
            spr.playing = False
            self.sprites.append(spr)
        if self.image != EMPTY_PIXEL:
            self.update_sprites()

    def get_h_bounds(self):
        h_bounds: List[float] = []

        if self.horizontal_bounds.x != -1:
            h_bounds.append(self.horizontal_bounds.x)
        else:
            h_bounds.append(0)

        if self.horizontal_bounds.y != -1:
            h_bounds.append(self.horizontal_bounds.y)
        else:
            h_bounds.append(self.screen_size.x)

        return h_bounds

    def get_v_bounds(self):
        v_bounds: List[float] = []

        if self.vertical_bounds.x != -1:
            v_bounds.append(self.vertical_bounds.x)
        else:
            v_bounds.append(0)

        if self.vertical_bounds.y != -1:
            v_bounds.append(self.vertical_bounds.y)
        else:
            v_bounds.append(self.screen_size.x)

        return v_bounds

    def is_h_part_in_bounds(self, h_part: int):
        if self.out_of_h_bounds:
            return False
        coords = Vector2(
            self.pos.x + (self.get_width() / self.h_parts) * h_part,
            self.pos.y
        )
        size = Vector2(
            self.get_width() / self.h_parts,
            self.get_height()
        )
        h_bounds = self.get_h_bounds()

        if coords.x > h_bounds[1] - 1 or coords.x + size.x < h_bounds[0] + 1:
            return False
        return True

    def get_movement(self):
        return Vector2(
            self.pos.x - self.last_pos.x,
            self.pos.y - self.last_pos.y
        )

    def apply_coords(self):
        last_x = self.pos.x
        for i in range(self.h_parts):
            sprite = self.sprites[i]
            sprite.x = last_x
            sprite.y = self.pos.y
            last_x = sprite.x + sprite.width

    def set_curr_frame(self, curr_frame: int):
        full = getattr(self, '_full_image', None)
        if full is None and self.sprites:
            full = self.sprites[0].image
        if full is None:
            return
        for i in range(self.h_parts):
            spr = self.sprites[i]
            frame_w = self.get_width()
            slice_start = int(curr_frame * frame_w + i * frame_w / self.h_parts)
            if i < self.h_parts - 1:
                slice_end = int(curr_frame * frame_w + (i + 1) * frame_w / self.h_parts)
            else:
                slice_end = (curr_frame + 1) * frame_w
            w = slice_end - slice_start
            if w <= 0:
                continue
            spr.image = full.subsurface(pygame.Rect(slice_start, 0, w, self.get_height()))
            spr.width = w
            spr.curr_frame = 0

    def animate(self):
        if self.playing:
            curr_frame = int(self.time_elapsed / self.frame_duration) % self.total_frames
            self.set_curr_frame(curr_frame)

    def render(self):
        if not self.visible:
            return
        for i in range(self.h_parts):
            if self.is_h_part_in_bounds(i):
                self.sprites[i].draw()

    def update_sprites(self, grow_a_bit: bool = False):
        if not self.sprites:
            return
        width = int(self.get_width() * self.total_frames)
        height = int(self.get_height())
        for i, spr in enumerate(self.sprites):
            spr.image = get_image(self.image, width, height)
            spr.width = int(self.get_width() / self.h_parts)
            spr.height = height
            spr.curr_frame = i
        if self.sprites:
            self._full_image = self.sprites[0].image.copy()

    def update(self):
        self.last_pos.x = self.pos.x
        self.last_pos.y = self.pos.y

        self.delta_time = get_screen().window.delta_time()
        self.time_elapsed += self.delta_time

        self.screen_size.x = REF_RES[0] * res_scale[0]
        self.screen_size.y = REF_RES[1] * res_scale[1]

        if self.total_frames == 1 and self.playing:
            self.playing = False

        self.animate()
        for spr in self.sprites:
            spr.update()

        if self.anchor != self:
            anchor_movement = self.anchor.get_movement()
            self.pos.x -= anchor_movement.x * self.offset_multiplier
            self.pos.y -= anchor_movement.y * self.offset_multiplier

    def destroy(self):
        self.instance_counter[0] -= 1

    def is_hovered(self):
        if get_screen().get_tab() not in self.get_tabs():
            return False

        mouse_pos = Vector2()
        mouse_pos.x, mouse_pos.y = self._mouse.get_position()

        if mouse_pos.x >= self.pos.x and mouse_pos.x <= self.pos.x + self.get_width() and \
                mouse_pos.y >= self.pos.y and mouse_pos.y <= self.pos.y + self.get_height():
            return True
        return False

    def is_pressed(self, button: int = 1):
        return self.is_hovered() and self._mouse.is_button_pressed(button)

    def is_just_pressed(self, button: int = 1):
        return self.is_hovered() and self._mouse.is_button_just_pressed(button)
