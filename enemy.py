from math import cos, sin

from body import Screen
from nave import *
from pplay.animation import Animation


class EnemyBullet(Bullet):
    def __init__(self, img: str, tab: int, objs: list):
        super().__init__(img, tab, objs)
        self.tags.append("enemy_projectile")
        self.velocity.y = 200
        

class Enemy(Nave):
    def __init__(self, img: str, width: int, height: int, tab: int, objs: list):
        super().__init__(img, width, height, tab, objs)
        if "player" in self.tags:
            self.tags.remove("player")
        self.tags.append("enemy")
        self.damage_from_tags = {"player_projectile"}
        self.health = 3
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = True
        self.speed = 400
        self.shooting_interval = 2
        
        self.default_health = 4
        self.health = 4
        
        self.hitbox = Vector2(-1,-1)
        
    def get_direction(self):
        self.direction.y = 1
    
    def spawn_rastro(self):
        self.rastro : Rastro = Rastro(self._tab, 8)

    def apply_rastro_offset(self):
        try:
            self.rastro
        except:
            self.spawn_rastro()
        self.rastro.offset = Vector2(self.get_width()/2, 0)
    
    def check_shoot(self):
        if self.shooting_cooldown <= 0:
            self.shoot()
            self.shooting_cooldown = self.shooting_interval
            
    def shoot(self):
        self.bullets.append(EnemyBullet(self.bullet_img, self._tab, self.objs))
        self.bullets[-1].x = self.x + self.get_width()/2 - self.bullets[-1].get_width()/2
        self.bullets[-1].y = self.y + self.get_height() - 5
        self.bullets[-1].horizontal_bounds = self.horizontal_bounds
        self.bullets[-1].side = self.side

class EnemySin(Enemy):
    """Inimigo com um padrao de movimento horizontal seno"""
    def __init__(self, img: str, width: int, height: int, tab: int, objs: list):
        super().__init__(img, width, height, tab, objs)
        self.sin_speed : float = 1
    
    def get_direction(self):
        self.direction.y = 1
        self.direction.x = cos(self._animation_time_elapsed * self.sin_speed)