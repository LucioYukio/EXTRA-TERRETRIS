from math import sqrt
from typing import Dict, Set

import perf
from effect import Effect
from screen import Object, List, Vector2, get_screen, res_scale

# side : List[body]
bodies : Dict = {
    0 : [],
    1 : []
}

class Body(Object):
    def __init__(self, image : str, width : int, height: int, side: int, tabs: List[int], h_parts: int = 1, z: int = 0):
        super().__init__(image, width, height, tabs, h_parts, z=z)
        ## Screen vai fazer com que nao saia da tela
        self.keep_in_bounds = True
        # variaveis de fisica
        self.velocity : Vector2 = Vector2(0,0)
        ## para detectar colisao
        self.objs = get_screen()._objs
        # se True, bate em objetos ao colidir
        self.stop_on_collision : bool = False
        # custom hitbox, se for -1, sera desconsiderada.
        self.hitbox : Vector2 = Vector2(-1,-1)

        self.radius : float = max(width, height)/2
        
        self.offset_multiplier = 1

        self.explosion_info : Dict = {
            "img" : "assets/images/explosion.png",
            "frames" : 8,
            "duration" : 1,
            "width" : width,
            "height" : width
        }

        self.side : int = side # "parte da tela" que o corpo pertence
        
        bodies[side].append(self)

    def get_hitbox(self):
        if self.hitbox.x != -1 and self.hitbox.y != -1: # if hitbox is valid
            return self.hitbox
        # if hitbox is invalid, interpret size as hitbox.
        return Vector2(self.get_width()/2, self.get_height()/2)

    def is_colliding_with_body(self, body: Object):
        perf.count("collision_checks")
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
        else:
            return False

    @staticmethod
    def do_hitboxes_overlap(coords1 : Vector2, hitbox1: Vector2, coords2 : Vector2, hitbox2 : Vector2):
        """Expects two centers and two hitboxes"""
        return (
            coords1.x - hitbox1.x <= coords2.x + hitbox2.x and
            coords1.x + hitbox1.x >= coords2.x - hitbox2.x and
            coords1.y - hitbox1.y <= coords2.y + hitbox2.y and
            coords1.y + hitbox1.y >= coords2.y - hitbox2.y
        )

    def get_collider(self):
        perf.count("get_collider_calls")
        perf.start("collision")
        for obj in bodies[self.side]:
            if self.is_colliding_with_body(obj):
                perf.stop("collision")
                return obj
        perf.stop("collision")
        return None

    def get_colliders(self, tags_to_check: Set[str]):
        perf.count("get_colliders_calls")
        perf.start("collisions")
        objs = []
        for obj in bodies[self.side]:
            if isinstance(obj, Body):
                # check for distance
                distance = sqrt(((self.pos.x + self.get_width()/2) - (obj.pos.x + obj.get_width()/2))**2 +
                                ((self.pos.y + self.get_height()/2) - (obj.pos.y + obj.get_height()/2))**2)
                if distance > self.radius and distance > obj.radius:
                    continue
                # check for tags
                valid : bool = False
                if tags_to_check:
                    for tag in tags_to_check:
                        if tag in obj.tags:
                            valid = True
                            break
                else:
                    valid = False
                #--------------
                if valid:
                    if self.is_colliding_with_body(obj):
                        objs.append(obj)
        perf.stop("collisions")
        return objs

    def collide(self, body: Object | None):
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
        self.pos.x += self.velocity.x * self.delta_time * res_scale[0]
        self.pos.y += self.velocity.y * self.delta_time * res_scale[1]
        # encostar no objeto, fazer de maneira mais optimizada depois (?)
        if self.get_collider() and self.stop_on_collision:
            self.pos.x = x
            self.pos.y = y
            self.collide(self.get_collider())

    def spawn_explosion(self):
        explosion : Effect = Effect(
            self.explosion_info["img"],
            self.explosion_info["frames"],
            self.explosion_info["duration"],
            self.explosion_info["width"],
            self.explosion_info["height"],
            self.get_tabs()
        )
        
        target_coords : Vector2 = self.get_center()
        target_coords.x -= explosion.get_width()/2
        target_coords.y -= explosion.get_height()/2
        
        explosion.pos.x = target_coords.x
        explosion.pos.y = target_coords.y
        if self.anchor != self:
            explosion.anchor = self.anchor
            explosion.offset_multiplier = self.offset_multiplier

    def update(self):
        super().update()
        perf.count("bodies_updated")
        self.apply_velocity()
    
    def destroy(self):
        super().destroy()
        bodies[self.side].remove(self)