from random import random
from typing import List

import pplay.window as w
import pplay.gameimage as gi
import pplay.keyboard as k
import pygame.transform
from engine.const import REF_RES, EMPTY_PIXEL, clamp, get_screen
from engine.mouse import Mouse
from engine.object import Object
from engine.vector2 import Vector2


class Screen:
    def __init__(self, width: int, height: int):
        self.window = w.Window(width, height)
        self._objs: List[Object] = []
        self._tab = 0
        self.bg_image = ""
        self._id_counter = 0
        self.mouse = Mouse()
        self.keyboard = k.Keyboard()
        self.bg_colors = {}
        self.bg_imgs = {}

        self.bg = gi.GameImage(EMPTY_PIXEL)

        self.ticks = 0
        self.time_elapsed = 0

        self.set_tab(0)

        self.window.draw_text("Carregando...", 100, 100)
        self.window.update()

    def set_tab(self, tab: int):
        self._tab = tab
        self.set_bg_image()

    def get_tab(self):
        return self._tab

    def set_bg_image(self):
        if self.bg_imgs.get(self._tab):
            self.bg.image = pygame.transform.scale(
                gi.GameImage(self.bg_imgs[self._tab]).image,
                (self.window.width, self.window.height)
            )

    def set_title(self, title: str):
        self.window.set_title(title)

    def add_object(self, obj: Object):
        obj.set_id(self._id_counter)
        self._id_counter += 1

        n = len(self._objs)
        i = 0
        inserted = False
        while i < n:
            if self._objs[i].z > obj.z:
                self._objs.insert(i, obj)
                inserted = True
                break
            i += 1
        if not inserted:
            self._objs.append(obj)

        return obj

    def order_objs_by_z(self):
        self._objs.sort(key=lambda obj: obj.z)

    def remove_object_by_id(self, id: int):
        for obj in self._objs:
            if obj.get_id() == id:
                obj.destroy()
                obj.dead = True
                self._objs.remove(obj)
                return

    def clear_tab(self, tab: int):
        ids_to_remove = [obj.get_id() for obj in self._objs if tab in obj.get_tabs()]
        for obj_id in ids_to_remove:
            self.remove_object_by_id(obj_id)

    def get_objs_with_tags(self, tags: List[str]):
        objs: List[Object] = []
        for obj in self._objs:
            if isinstance(obj, Object):
                is_equal = True
                for tag in obj.tags:
                    if tag not in tags:
                        is_equal = False
                        break
                if is_equal:
                    objs.append(obj)
        return objs

    def get_objs_in_tab(self, tab):
        objs: List[Object] = []
        for obj in self._objs:
            if isinstance(obj, Object) and tab in obj.get_tabs():
                objs.append(obj)
        return objs

    def render(self):
        for obj in self._objs:
            if obj.visible and self.get_tab() in obj.get_tabs():
                obj.render()

    def update(self):
        if self.window.delta_time() > 0:
            self.time_elapsed += self.window.delta_time()
            self.ticks += 1

        if self.bg_colors.get(self._tab):
            self.window.set_background_color(self.bg_colors.get(self._tab, 0))
        else:
            self.window.set_background_color("black")

        if self.bg_imgs.get(self._tab):
            self.bg.draw()

        ids_to_remove: List[int] = []
        for obj in self._objs:
            if not isinstance(obj, Object) or get_screen().get_tab() not in obj.get_tabs() or not obj.enabled:
                continue
            if obj.wants_to_die:
                ids_to_remove.append(obj.get_id())
                continue
            
            
            obj.apply_coords()

            obj.delta_time = self.window.delta_time()

            h_bounds = Vector2(
                0 if obj.horizontal_bounds.x == -1 else obj.horizontal_bounds.x,
                REF_RES[0] if obj.horizontal_bounds.y == -1 else obj.horizontal_bounds.y,
            )

            v_bounds = Vector2(
                0 if obj.vertical_bounds.x == -1 else obj.vertical_bounds.x,
                REF_RES[1] if obj.vertical_bounds.y == -1 else obj.vertical_bounds.y,
            )

            obj.update()

            if obj.keep_in_bounds:
                obj.pos.x = clamp(obj.pos.x, h_bounds.x, h_bounds.y - obj.get_width())
                obj.pos.y = clamp(obj.pos.y, v_bounds.x, v_bounds.y - obj.get_height())
            else:
                obj.out_of_h_bounds = obj.pos.x > h_bounds.y or \
                    obj.pos.x + obj.get_width() < h_bounds.x
                obj.out_of_v_bounds = obj.pos.y > v_bounds.y or \
                    obj.pos.y + obj.get_height() < v_bounds.x

            obj.out_of_screen = ((obj.pos.x + obj.get_width() < h_bounds.x) or (obj.pos.x > h_bounds.y)) or \
                ((obj.pos.y + obj.get_height() < v_bounds.x) or (obj.pos.y > v_bounds.y))

            if obj.out_of_h_bounds and obj.destroy_out_of_h_bounds or \
                    obj.out_of_v_bounds and obj.destroy_out_of_v_bounds:
                ids_to_remove.append(obj.get_id())

        for obj_id in ids_to_remove:
            self.remove_object_by_id(obj_id)

        self.render()
        self.window.update()
