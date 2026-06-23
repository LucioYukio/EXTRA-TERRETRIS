from math import sqrt
from typing import Dict, List, Set

from config.sounds import EXPLOSAO
from entities.effect import Effect

from engine.object import Object
from engine.screen import get_screen
from engine.vector2 import Vector2

bodies: Dict = {
    0: [],
    1: []
}


class Body(Object):
    def __init__(self, image: str, width: int, height: int, side: int, tabs: List[int], h_parts: int = 1, z: int = 0):
        super().__init__(image, width, height, tabs, h_parts, z=z)
        self.keep_in_bounds = True
        self.velocity = Vector2(0, 0)
        self.objs = get_screen()._objs
        self.stop_on_collision = False
        self.hitbox = Vector2(-1, -1)

        self.radius = max(width, height) / 2

        self.offset_multiplier = 1

        self.explosion_info: Dict = {
            "img": "assets/images/explosion.png",
            "frames": 8,
            "duration": 1,
            "width": width,
            "height": width
        }

        self.side = side

        bodies[side].append(self)

    def get_hitbox(self):
        if self.hitbox.x != -1 and self.hitbox.y != -1:
            return self.hitbox
        return Vector2(self.get_width() / 2, self.get_height() / 2)

    def is_colliding_with_body(self, body: Object):
        if isinstance(body, Body):
            if self.side != body.side:
                return False
            if body is self:
                return False
            if get_screen().get_tab() not in self.get_tabs():
                return False
            if get_screen().get_tab() not in body.get_tabs():
                return False
            return self.do_hitboxes_overlap(
                self.get_center(),
                self.get_hitbox(),
                body.get_center(),
                body.get_hitbox()
            )
        return False

    @staticmethod
    def do_hitboxes_overlap(coords1: Vector2, hitbox1: Vector2, coords2: Vector2, hitbox2: Vector2):
        return (
            coords1.x - hitbox1.x <= coords2.x + hitbox2.x and
            coords1.x + hitbox1.x >= coords2.x - hitbox2.x and
            coords1.y - hitbox1.y <= coords2.y + hitbox2.y and
            coords1.y + hitbox1.y >= coords2.y - hitbox2.y
        )

    def get_collider(self):
        for obj in bodies[self.side]:
            if self.is_colliding_with_body(obj):
                return obj
        return None

    def get_colliders(self, tags_to_check: Set[str]):
        objs = []
        for obj in bodies[self.side]:
            if isinstance(obj, Body):
                distance = sqrt(
                    ((self.pos.x + self.get_width() / 2) - (obj.pos.x + obj.get_width() / 2)) ** 2 +
                    ((self.pos.y + self.get_height() / 2) - (obj.pos.y + obj.get_height() / 2)) ** 2
                )
                if distance > self.radius and distance > obj.radius:
                    continue
                valid = False
                if tags_to_check:
                    for tag in tags_to_check:
                        if tag in obj.tags:
                            valid = True
                            break
                else:
                    valid = False
                if valid:
                    if self.is_colliding_with_body(obj):
                        objs.append(obj)
        return objs

    def collide(self, body: 'Body | None'):
        if not body or not isinstance(body, Body):
            return
        self.velocity.x = self.velocity.x + body.velocity.x
        self.velocity.y = self.velocity.y + body.velocity.y
        body.velocity.x = self.velocity.x
        body.velocity.y = self.velocity.y

    def apply_velocity(self):
        if self.velocity.x == 0 and self.velocity.y == 0:
            return
        x, y = self.pos.x, self.pos.y
        self.pos.x += self.velocity.x * self.delta_time
        self.pos.y += self.velocity.y * self.delta_time
        if self.get_collider() and self.stop_on_collision:
            self.pos.x = x
            self.pos.y = y
            self.collide(self.get_collider())

    def spawn_explosion(self):
        explosion = Effect(
            self.explosion_info["img"],
            self.explosion_info["frames"],
            self.explosion_info["duration"],
            self.explosion_info["width"],
            self.explosion_info["height"],
            self.get_tabs()
        )

        target_coords = self.get_center()
        target_coords.x -= explosion.get_width() / 2
        target_coords.y -= explosion.get_height() / 2

        explosion.pos.x = target_coords.x
        explosion.pos.y = target_coords.y
        if self.anchor != self:
            explosion.anchor = self.anchor
            explosion.offset_multiplier = self.offset_multiplier

        EXPLOSAO.stop()
        EXPLOSAO.play()

    def update(self):
        super().update()
        self.apply_velocity()

    def destroy(self):
        super().destroy()
        bodies[self.side].remove(self)
