from pygame.math import lerp

from screen import *

class Body(Object):
    def __init__(self, image : str, width : int, height: int, tab: int, objs: list, h_parts: int = 1):
        super().__init__(image, width, height, tab, h_parts)
        ## Screen vai fazer com que nao saia da tela
        self.keep_in_bounds = True
        # variaveis de fisica
        self.velocity : Vector2 = Vector2(0,0)
        ## para detectar colisao
        self.objs = objs
        # se True, bate em objetos ao colidir
        self.stop_on_collision : bool = False
        # custom hitbox, se for -1, sera desconsiderada.
        self.hitbox : Vector2 = Vector2(-1,-1)
        
        self.side : int = 0

    def get_hitbox(self):
        if self.hitbox.x != -1 and self.hitbox.y != -1: # if hitbox is valid
            return self.hitbox
        # if hitbox is invalid, interpret size as hitbox.
        return Vector2(self.get_width()/2, self.get_height()/2)
    
    def is_colliding_with_body(self, body: Object):
        if not isinstance(body, Body) or self.side != body.side:
            return False
        if body is self:
            return False
        if body.get_tab() != self.get_tab():
            return False 
        return self.do_hitboxes_overlap(self.get_center(), self.get_hitbox(), body.get_center(), body.get_hitbox())
    
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
        for obj in self.objs:
            if self.is_colliding_with_body(obj):
                return obj
        return None

    def get_colliders(self):
        objs = []
        for obj in self.objs:
            if self.is_colliding_with_body(obj):
                objs.append(obj)
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
        x , y = self.x, self.y
        self.x += self.velocity.x * self.delta_time * res_scale[0]
        self.y += self.velocity.y * self.delta_time * res_scale[1]
        # encostar no objeto, fazer de maneira mais optimizada depois
        if self.get_collider() and self.stop_on_collision:
            self.x = x
            self.y = y
            self.collide(self.get_collider())
        
    def update(self):
        self.apply_velocity()
        super().update()