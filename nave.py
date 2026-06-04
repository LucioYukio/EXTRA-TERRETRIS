from typing import Dict

from body import *
from pplay.animation import Animation
from pplay.window import Window
from projectile import Projectile
from screen import *
from effect import Effect

DEFAULT_NAVE_SIZE : Vector2 = Vector2(69, 83)
DEFAULT_NAVE_HITBOX : Vector2 = Vector2(20, 30)

class Bullet(Projectile):
    def __init__(self, img: str, tabs: List[int], objs: list):
        super().__init__(img, 18, 18, tabs, objs)
        self.set_total_frames(4)
        self.frame_duration = 0.1
        
        self.explosion_info : Dict = {
            "img" : "assets/images/explosion.png",
            "frames" : 11,
            "duration" : 0.2,
            "width" : 48,
            "height" : 48
        }
        
        self.categorie = "bullet"
    
    def update(self):
        super().update()
        #print(self.horizontal_bounds)
    
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

class NaveBullet(Bullet):
    def __init__(self, img: str, tabs: List[int], objs: list):
        super().__init__(img, tabs, objs)
        self.tags.append("player_projectile")
        self.velocity.y = -600
        
        self.categorie = "nave bullet"
        
        #self.explosion_info["img"] = "assets/images/explosion_red.png"

class Rastro(Object):
    def __init__(self, tabs: List[int], rastros: int):
        # implementar intervalo: espera "intervalo" cooldown para fazer as trocas
        super().__init__(EMPTY_PIXEL,8, 8, tabs)
        
        self.rastros : List[Object] = [] # do mais fino pro mais grosso
        self.qtd = rastros
        
        self.offset : Vector2 = Vector2(0,0)
        
        self.interval : float = 0.075 # interval between rastros changing position
        self.cooldown : float = 0 # changing rastros cooldown
        
        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = False
        self.keep_in_bounds = False
        
        for i in range(rastros):
            rastro : Object = Object(
                "assets/images/rastro.png",
                int(self._width * i / rastros + 2),
                int(self._height * i / rastros + 2),
                tabs,
                2
            )
            rastro.destroy_out_of_h_bounds = False
            rastro.destroy_out_of_v_bounds = False
            rastro.horizontal_bounds = self.horizontal_bounds
            rastro.categorie = "rastrinho"
            rastro.keep_in_bounds = False
            self.rastros.append(rastro)
        
        self.categorie = "rastro"
    
    def update(self):
        self.cooldown += self.delta_time
        if self.cooldown > self.interval:
            self.advance_rastro()
            self.cooldown = 0
    
    def propagate_bounds(self):
        for r in self.rastros:
            r.horizontal_bounds = self.horizontal_bounds
            pass
    
    def advance_rastro(self):
        if self.qtd <= 0:
            return 
        self.rastros[-1].pos.x = self.pos.x + self.offset.x - self._width/2
        self.rastros[-1].pos.y = self.pos.y + self.offset.y - self._height + 1
        for i in range(self.qtd - 1):
            self.rastros[i].pos.x = self.rastros[i+1].pos.x + self.rastros[i+1].get_width()/2 - self.rastros[i].get_width()/2
            self.rastros[i].pos.y = self.rastros[i+1].pos.y + self.rastros[i+1].get_height()/2 - self.rastros[i].get_height()/2
    
    def render(self):
        return
    
    def destroy(self):
        for rastro in self.rastros:
            rastro.wants_to_die = True

class Nave(Body):
    
    rastro : Rastro
    
    def __init__(self, image: str, width: int, height: int, tabs: List[int], objs: list, h_parts: int = 16):
        super().__init__(image, width, height, tabs, objs, h_parts)
        self.tags.append("player")
        self.damage_from_tags = {"enemy_projectile"}
        self.keyboard = get_screen().keyboard
        self.speed : float = 300
        self.direction : Vector2 = Vector2(0,0)
        self.hitbox = DEFAULT_NAVE_HITBOX.copy()
        
        """Stats vars"""
        self.default_health : float = 9999
        self.health : float = 9999
        self.score : int = 0
        # tempo ate poder levar dano de novo
        self.damage_interval : float = 1
        self.damage_cooldown : float = 0
        
        self.explosion_info : Dict = {
            "img" : "assets/images/explosion.png",
            "frames" : 11,
            "duration" : 2,
            "width" : 128,
            "height" : 128
        }
        
        """Bullet vars"""
        self.bullet_img : str = "assets/images/bullet_white.png"
        self.default_shooting_interval : float = 0.2
        self.shooting_interval : float = self.default_shooting_interval
        self.shooting_cooldown : float = 0
        self.bullets : List[Bullet] = []
        
        """Teclas"""
        self.UP    : str = "up"
        self.DOWN  : str = "down"
        self.LEFT  : str = "left"
        self.RIGHT : str = "right"
        self.SHOOT : str = "space"
        self.POWER : str = "x"
        # Se esta apertando left e right e se esta apertando up and down, para x e y respectivamente
        self.pressing_both : Vector2 = Vector2(0,0)
        
        self.categorie = "nave"
    
    def shoot(self):
        self.bullets.append(NaveBullet(self.bullet_img, self.get_tabs(), self.objs))
        self.bullets[-1].pos.x = self.pos.x + self.get_width()/2 - self.bullets[-1].get_width()/2
        self.bullets[-1].pos.y = self.pos.y - self.bullets[-1].get_height() + 5
        self.bullets[-1].horizontal_bounds = self.horizontal_bounds
        self.bullets[-1].side = self.side

    def spawn_rastro(self):
        self.rastro = Rastro(self.get_tabs(), 8)
        self.rastro.horizontal_bounds = self.horizontal_bounds
        for r in self.rastro.rastros:
            r.horizontal_bounds = self.horizontal_bounds
        self.apply_rastro_offset()

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
    
    def apply_rastro_offset(self):
        try:    self.rastro
        except: self.spawn_rastro()
        # para baixo da nave
        self.rastro.offset = Vector2(self.get_width()/2, self.get_height())
    
    def set_height(self, height: float):
        super().set_height(height)
        self.apply_rastro_offset()
    
    def set_width(self, width: float):
        super().set_width(width)
        self.apply_rastro_offset()
    
    def get_direction(self):
        # Se apertar ambos os botoes, trocar direcao
        direction_x = self.keyboard.key_pressed(self.RIGHT) - self.keyboard.key_pressed(self.LEFT)
        if self.keyboard.key_pressed(self.RIGHT) and self.keyboard.key_pressed(self.LEFT):
            if self.pressing_both.x == 0:
                # pressionando ambos, mudar para a mais recente
                self.pressing_both.x = 1
                self.direction.x *= -1
            if self.direction.x < 0:
                self.direction.x = -1
            else:
                self.direction.x = 1
                
        else:
            self.pressing_both.x = False
            self.direction.x = direction_x
        
        direction_y = self.keyboard.key_pressed(self.DOWN) - self.keyboard.key_pressed(self.UP)
        if self.keyboard.key_pressed(self.DOWN) and self.keyboard.key_pressed(self.UP):
            if self.pressing_both.y == 0:
                # pressionando ambos, mudar para a mais recente
                self.pressing_both.y = 1
                self.direction.y *= -1
            if self.direction.y < 0:
                self.direction.y = -1
            else:
                self.direction.y = 1
        else:
            self.pressing_both.y = False
            self.direction.y = direction_y
        
    def check_shoot(self):
        if self.keyboard.key_pressed(self.SHOOT) and self.shooting_cooldown <= 0:
            self.shoot()
            self.shooting_cooldown = self.shooting_interval
    
    def destroy_rastro(self):
        if not hasattr(self, "rastro"):
            return
        self.rastro.wants_to_die = True
    
    def destroy(self):
        self.rastro.wants_to_die
        for r in self.rastro.rastros:
            r.wants_to_die = True
    
    def check_damage(self):
        colliders = self.get_colliders()
        for c in colliders:
            if isinstance(c, Projectile):
                if self.damage_from_tags and not any(tag in c.tags for tag in self.damage_from_tags):
                    continue
                if c in self.bullets:
                    continue
                # receive damage
                self.health -= c.get_damage()
                c.wants_to_die = c.destroy_on_hit
                if c.destroy_on_hit and isinstance(c, Bullet):
                    c.spawn_explosion()
        if self.health <= 0:
            self.spawn_explosion()
            self.wants_to_die = True

    def destroy_bullet(self, bullet: Bullet):
        bullet.wants_to_die = True
        self.bullets.remove(bullet)
    
    def propagate_bounds(self):
        self.rastro.horizontal_bounds = self.horizontal_bounds
        self.rastro.propagate_bounds()
    
    def update(self):
        if self.rastro.horizontal_bounds != self.horizontal_bounds:
            self.propagate_bounds()
        
        self.get_direction()
        
        self.direction.normalize()
        self.velocity.x = self.direction.x * self.speed
        self.velocity.y = self.direction.y * self.speed
        
        self.check_shoot()
        self.check_damage()
        
        for b in self.bullets:
            if b.wants_to_die or (b.destroy_out_of_screen and b.out_of_screen):
                self.destroy_bullet(b)
        
        self.shooting_cooldown = max(self.shooting_cooldown - self.delta_time, 0)
        
        self.rastro.pos.x = self.pos.x
        self.rastro.pos.y = self.pos.y
        self.rastro.delta_time = self.delta_time
        self.rastro.update()
        
        super().update()
