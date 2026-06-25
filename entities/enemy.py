from math import cos
from typing import List

from entities.bullets import FollowingBullet
from entities.nave import Nave
from engine.object import Object
from engine.vector2 import Vector2


class EnemyBullet(FollowingBullet):
    def __init__(self, img: str, side: int, tabs: List[int], target: Object, turning_speed: float):
        super().__init__(img, side, target, turning_speed, tabs)
        self.tags.append("enemy_projectile")
        self.speed = 150
        self.direction.y = 1
        self.destroy_out_of_h_bounds = False


class Enemy(Nave):
    def __init__(self, img: str, width: int, height: int, side: int, target: Object, tabs: List[int]):
        super().__init__(img, width, height, side, tabs)
        if "player" in self.tags:
            self.tags.remove("player")
        self.tags.append("enemy")
        self.damage_from_tags = {"player_projectile", "asteroid"}
        self.health = 3
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = True
        self.speed = 200

        self.shooting_interval = 1

        self.target = target
        self.bullet_turning_speed = 3 / 100

        self.offset_multiplier = 1

        self.default_health = 4
        self.health = 4

        self.damage_interval = 0

        self.hitbox = Vector2(-1, -1)

        self.points_value = 10
        self.points_list: List[int] = [0, 0]

        self.bullet_speed_mult = 1

    def get_direction(self):
        self.direction.y = 1

    def apply_rastro_offset(self):
        try:
            self.rastro
        except AttributeError:
            self.spawn_rastro()
        self.rastro.offset = Vector2(self.get_width() / 2, 0)

    def check_shoot(self):
        if self.shooting_cooldown <= 0:
            self.shoot()
            self.shooting_cooldown = self.shooting_interval

    def spawn_bullet(self):
        self.bullets.append(EnemyBullet(self.bullet_img, self.side, self.get_tabs(), self.target, self.bullet_turning_speed))
        self.bullets[-1].pos.x = self.pos.x + self.get_width() / 2 - self.bullets[-1].get_width() / 2
        self.bullets[-1].pos.y = self.pos.y + self.get_height() - 5
        self.bullets[-1].speed *= self.bullet_speed_mult

    def spawn_rastro(self):
        super().spawn_rastro()
        self.rastro.speed = -400

    def destroy(self):
        super().destroy()
        self.points_list[self.side] += self.points_value


class EnemySin(Enemy):
    def __init__(self, img: str, width: int, height: int, side: int, target: Object, tabs: List[int]):
        super().__init__(img, width, height, side, target, tabs)
        self.sin_speed = 1

    def get_direction(self):
        self.direction.y = 1
        self.direction.x = cos(self.time_elapsed * self.sin_speed)

class SpinEnemy(Enemy):
    def __init__(self, width: int, height: int, side: int, target: Object, tabs: List[int]):
        super().__init__(f"assets/images/spin_enemy_{"purple" if side == 0 else "green"}.png", width, height, side, target, tabs)
        self.set_total_frames(8)
        # chance de atirar a cada mudanca de frame
