from math import acos, asin, atan2, cos, pi, sin
from random import random
from typing import List

from engine.const import clamp
from entities.bullets import Bullet, FollowingBullet
from entities.nave import Nave
from engine.object import Object
from engine.vector2 import Vector2


class EnemyBullet(Bullet):
    def __init__(self, img: str, side: int, tabs: List[int]):
        super().__init__(img, side, tabs)
        self.tags.append("enemy_projectile")
        self.speed = 150
        self.direction.y = 1

class FollowingEnemyBullet(FollowingBullet):
    def __init__(self, img: str, side: int, tabs: List[int], target: Object, turning_speed: float):
        super().__init__(img, side, target, turning_speed, tabs)
        self.tags.append("enemy_projectile")
        self.speed = 150
        self.direction.y = 1

class SpinningEnemyBullet(Bullet):
    def __init__(self, side: int, tabs: List[int]):
        super().__init__(
            f"assets/images/spinning_bullet_{'green' if side == 0 else 'purple'}.png", 
            side, tabs)
        self.tags.append("enemy_projectile")
        self.set_total_frames(8)    
        self.speed = 250
        
        self.set_width( 20)
        self.set_height(20)

class Enemy(Nave):
    def __init__(self, width: int, height: int, side: int, target: Object, tabs: List[int], image: str = ""):
        super().__init__(f"assets/images/nave_inimiga_{'verde' if side == 0 else 'roxa'}.png" if image == "" else image, width, height, side, tabs)
        if "player" in self.tags:
            self.tags.remove("player")
            
        self.set_total_frames(7)
        self.set_curr_frame(4)
        self.playing = False
            
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

    def update(self):
        super().update()
        self.set_curr_frame(int((self.direction.x/2+0.5) * 7))
        self.rastro.pos.x = self.pos.x - self.direction.x * self.get_width()/2

    def check_shoot(self):
        if self.shooting_cooldown <= 0:
            self.shoot()
            self.shooting_cooldown = self.shooting_interval

    def spawn_bullet(self):
        self.bullets.append(FollowingEnemyBullet(self.bullet_img, self.side, self.get_tabs(), self.target, self.bullet_turning_speed))
        self.bullets[-1].pos.x = self.pos.x + self.get_width() / 2 - self.bullets[-1].get_width() / 2
        self.bullets[-1].pos.y = self.pos.y + self.get_height() - 5
        self.bullets[-1].speed *= self.bullet_speed_mult
        self.bullets[-1].direction = self.direction.copy()

    def spawn_rastro(self):
        super().spawn_rastro()
        self.rastro.speed = -400

    def destroy(self):
        super().destroy()
        self.points_list[self.side] += self.points_value


class EnemySin(Enemy):
    def __init__(self, width: int, height: int, side: int, target: Object, tabs: List[int]):
        super().__init__(width, height, side, target, tabs)
        self.sin_speed = 0.5
        self.speed = 300
        self.shooting_interval *= 0.5

    def get_direction(self):
        self.direction.y = 1
        self.direction.x = cos(self.time_elapsed * self.sin_speed)

class SpinEnemy(Enemy):
    def __init__(self, width: int, height: int, side: int, target: Object, tabs: List[int]):
        super().__init__(width, height, side, target, tabs, f"assets/images/spin_enemy_{'green' if side == 0 else 'purple'}.png")
        self.set_total_frames(8)
        # chance de atirar a cada mudanca de frame
        self.last_curr_frame : int = 0 # se diferente de curr_sprite, ver se atira
        self.chance_to_shoot : float = 1/120
        self.last_time_shot : float = 0
        
        self.frame_duration = 1/20
        
        self.speed = 100
        self.default_health *= 10
        self.health = self.default_health
        self.points_value *= 10
    
    def spawn_bullet(self):
        self.bullets.append(SpinningEnemyBullet(self.side, self.get_tabs()))
        self.bullets[-1].pos = self.get_center()
        self.bullets[-1].z = self.z+1
    
    def update(self):
        super().update()
        
        target_direction : Vector2 = self.pos.look_at(self.target.pos)
        target_direction.normalize()
        
        rotation = atan2(target_direction.y, target_direction.x) / pi
        
        if rotation < 0:
            rotation = 2 + rotation
        rotation /= 2
        rotation = 1-rotation
        
        if (self.side == 0):
            print(( rotation))
        self.set_curr_frame(
            clamp(round(rotation * 8), 0, 7)
        )
    
    def shoot(self):
        super().shoot()
        
        if not self.bullets:
            return
        
        b = self.bullets[-1]
        b.pos = self.get_center()
        
        b.direction = self.pos.look_at(self.target.pos)
        b.direction.normalize()
        
        b.pos += b.direction * b.get_width()
    
    def check_shoot(self):
        if random() <= self.chance_to_shoot:
            self.shoot()
        
class FastEnemy(EnemySin):
    pass