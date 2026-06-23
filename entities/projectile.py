from typing import List

from entities.body import Body
from engine.vector2 import Vector2


class Projectile(Body):
    def __init__(self, image: str, width: int, height: int, side: int, tabs: List[int], h_parts: int = 1):
        super().__init__(image, width, height, side, tabs, h_parts)
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = True
        self.destroy_out_of_v_bounds = True
        self.damage = 1
        self.destroy_out_of_screen = True
        self.destroy_on_hit = True
        self.wants_to_die = False
        self.tags.append("projectile")

        self.direction = Vector2()
        self.speed = 1

        self.categorie = "projectile"

    def get_damage(self):
        return self.damage

    def update(self):
        self.direction.normalize()
        self.velocity = self.direction * self.speed
        super().update()
