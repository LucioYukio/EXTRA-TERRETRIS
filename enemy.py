from math import cos, sin

from body import Screen
from nave import *
from pplay.animation import Animation


class EnemyBullet(FollowingBullet):
    def __init__(self, img: str, tabs: List[int], target: Object, turning_speed: float):
        super().__init__(img, target, turning_speed, tabs)
        self.tags.append("enemy_projectile")
        self.speed = 200
        self.direction.y = 1
        

class Enemy(Nave):
    def __init__(self, img: str, width: int, height: int, target: Object, tabs: List[int]):
        super().__init__(img, width, height, tabs)
        if "player" in self.tags:
            self.tags.remove("player")
        self.tags.append("enemy")
        self.damage_from_tags = {"player_projectile"}
        self.health = 3
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = True
        self.speed = 100
        self.shooting_interval = 2
        
        self.target : Object = target
        self.bullet_turning_speed : float = 0.005
        
        self.offset_multiplier = 0.5
        
        self.default_health = 4
        self.health = 4
        
        self.hitbox = Vector2(-1,-1)
        
        self.points_value : int = 10 # pontos que player recebe ao matar esse inimigo
        self.points_list : List[int] = [0,0] # linkar (=) lista de pontos (aura) usado
        
    def get_direction(self):
        self.direction.y = 1

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
            
    def spawn_bullet(self):
        self.bullets.append(EnemyBullet(self.bullet_img, self.get_tabs(), self.target, self.bullet_turning_speed))
        self.bullets[-1].pos.x = self.pos.x + self.get_width()/2 - self.bullets[-1].get_width()/2
        self.bullets[-1].pos.y = self.pos.y + self.get_height() - 5

    def destroy(self):
        super().destroy()
        self.points_list[self.side] += self.points_value

class EnemySin(Enemy):
    """Inimigo com um padrao de movimento horizontal seno"""
    def __init__(self, img: str, width: int, height: int, target: Object, tabs: List[int]):
        super().__init__(img, width, height, target, tabs)
        self.sin_speed : float = 1
    
    def get_direction(self):
        self.direction.y = 1
        self.direction.x = cos(self.time_elapsed * self.sin_speed)
