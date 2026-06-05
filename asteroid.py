from typing import Dict

from effect import Effect
from nave import Bullet
from projectile import *
from screen import List

class Asteroid(Projectile):
    def __init__(self, width: int, height: int, total_health: float, tabs: List[int]):
        super().__init__("assets/images/spinning_asteroid.png", width, height, tabs, 6)
        
        self.set_total_frames(59)
        self.frame_duration = (1/24)
        self.playing = True
        
        self.direction.y = 1
        self.speed = 200
        
        self.hitbox = Vector2(width/2* 0.775, height/2* 0.775) # tem que ser um pouco menor
        
        self.keep_in_bounds          = False
        self.destroy_out_of_screen   = False
        self.destroy_out_of_v_bounds = False
        self.destroy_out_of_h_bounds = False
        self.destroy_on_hit          = False
        
        self.damage_from_tags = {"enemy_projectile", "player_projectile"}
        
        self.total_health : float = total_health
        self.health : float = total_health
        self.dead : bool = False
        
        self.points_value : int = 10 # pontos que player recebe ao matar esse inimigo
        self.points_list : List[int] = [0,0] # linkar (=) lista de pontos (aura) usado
        
        self.reset_timer: float = 0 # tempo que esse asteroid ficou abaixo da tela
        
        self.categorie = "asteroid"
        self.tags.append("asteroid")
    
    def check_damage(self):
        colliders = self.get_colliders()
        for c in colliders:
            if isinstance(c, Bullet):
                # destroy bullet
                c.wants_to_die = c.destroy_on_hit
                if c.destroy_on_hit and isinstance(c, Bullet):
                    c.spawn_explosion()
                # take damage
                self.health -= c.damage
                if self.health <= 0:
                    self.die()
    
    def die(self):
        """get out of screen, restore health and spawn debris"""
        self.spawn_explosion()
        self.spawn_debri()
        self.pos.y = TELA_H
        self.health = self.total_health
        self.points_list[self.side] += self.points_value
        
    
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
    
    def spawn_debri(self):
        pass
    
    def destroy(self):
        super().destroy()
        print("destroyed")
    
    def update(self):
        super().update()
        self.check_damage()
        if self.pos.y >= TELA_H:
            self.reset_timer += self.delta_time
        else:
            self.reset_timer = 0