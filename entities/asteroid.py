from typing import List

from config.sounds import ASTEROIDE
from entities.bullets import Bullet
from entities.effect import Effect
from entities.projectile import Projectile
from engine.const import TELA_H
from engine.vector2 import Vector2


class Debri(Projectile):
    def __init__(self, image, width: int, height: int, side: int, total_health: float, tabs: List[int]):
        super().__init__(image, width, height, side, tabs, 6)

        self.set_total_frames(59)
        self.frame_duration = 1 / (24 * 4)
        self.playing = True

        self.speed = 300

        self.hitbox = Vector2(width / 2 * 0.775, height / 2 * 0.775)

        self.keep_in_bounds = False
        self.destroy_out_of_screen = False
        self.destroy_out_of_h_bounds = False

        self.destroy_out_of_v_bounds = True
        self.destroy_on_hit = True

        self.damage_from_tags = {"enemy_projectile", "player_projectile"}

        self.health = total_health

        self.points_value = 10
        self.points_list: List[int] = [0, 0]

        self.categorie = "debri"
        self.tags.append("debri")

    def check_damage(self):
        colliders = self.get_colliders(self.damage_from_tags)
        for c in colliders:
            if isinstance(c, Bullet):
                c.wants_to_die = c.destroy_on_hit
                if c.destroy_on_hit and isinstance(c, Bullet):
                    c.spawn_explosion()
                self.health -= c.damage
                if self.health <= 0:
                    self.wants_to_die = True

    def update(self):
        super().update()
        self.check_damage()


class Asteroid(Projectile):
    def __init__(self, width: int, height: int, side: int, total_health: float, tabs: List[int]):
        super().__init__("assets/images/spinning_asteroid.png", width, height, side, tabs, 6)

        self.set_total_frames(59)
        self.frame_duration = 1 / 24
        self.playing = True

        self.direction.y = 1
        self.speed = 200

        self.hitbox = Vector2(width / 2 * 0.775, height / 2 * 0.775)

        self.keep_in_bounds = False
        self.destroy_out_of_screen = False
        self.destroy_out_of_v_bounds = False
        self.destroy_out_of_h_bounds = False
        self.destroy_on_hit = False

        self.damage_from_tags = {"enemy_projectile", "player_projectile"}

        self.total_health = total_health
        self.health = total_health

        self.points_value = 10
        self.points_list: List[int] = [0, 0]

        self.reset_timer = 0

        self.categorie = "asteroid"
        self.tags.append("asteroid")

    def check_damage(self):
        colliders = self.get_colliders(self.damage_from_tags)
        for c in colliders:
            if isinstance(c, Bullet):
                c.wants_to_die = c.destroy_on_hit
                if c.destroy_on_hit and isinstance(c, Bullet):
                    c.spawn_explosion()
                self.health -= c.damage
                if self.health <= 0:
                    self.die()

    def die(self):
        self.spawn_explosion()
        self.spawn_debris()
        self.pos.y = TELA_H
        self.health = self.total_health
        self.points_list[self.side] += self.points_value

    def spawn_explosion(self):
        super().spawn_explosion()
        ASTEROIDE.stop()
        ASTEROIDE.play()

    def spawn_debri(self, image: str, direction: Vector2):
        w, h = self.get_width() // 2, self.get_height() // 2
        debri = Debri(image, int(w), int(h), self.side, self.total_health // 4, self.get_tabs())
        direction.normalize()
        debri.direction = direction
        debri.speed = self.speed * 2
        debri.pos = self.get_center() - Vector2(w / 2, h / 2)
        debri.horizontal_bounds = self.horizontal_bounds

    def spawn_debris(self):
        self.spawn_debri("assets/images/spinning_debri_top_left.png", Vector2(-1, -1))
        self.spawn_debri("assets/images/spinning_debri_bottom_left.png", Vector2(-1, 1))
        self.spawn_debri("assets/images/spinning_debri_top_right.png", Vector2(1, 1))
        self.spawn_debri("assets/images/spinning_debri_bottom_right.png", Vector2(1, -1))

    def update(self):
        super().update()
        self.check_damage()
        if self.pos.y >= TELA_H:
            self.reset_timer += self.delta_time
        else:
            self.reset_timer = 0
