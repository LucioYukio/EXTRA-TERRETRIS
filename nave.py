from typing import Dict

from body import Body
from effect import Effect
from projectile import Projectile
from screen import Vector2, Object, List, get_screen, EMPTY_PIXEL

DEFAULT_NAVE_SIZE : Vector2 = Vector2(69, 83)
DEFAULT_NAVE_HITBOX : Vector2 = Vector2(20, 30)

class Bullet(Projectile):
    def __init__(self, img: str, side: int, tabs: List[int]):
        super().__init__(img, 18, 18, side, tabs)
        self.set_total_frames(4)
        self.frame_duration = 0.1
        
        self.explosion_info : Dict = {
            "img" : "assets/images/explosion_small.png",
            "frames" : 8,
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

class FollowingBullet(Bullet):
    """Follows the target, turning at turning speed.
    Keep turning speed between 0 and 1, or else it under/overshoots"""
    def __init__(self, img: str, side: int, target: Object, turning_speed: float, tabs: List[int]):
        super().__init__(img, side, tabs)
        self.target : Object = target
        self.turning_speed : float = turning_speed
        self.following_duration : float = 3 # after this, bullet does not follow target
        
    def update(self):
        if self.time_elapsed < self.following_duration:
            self.direction = self.direction.lerp(self.pos.look_at(self.target.get_center()), self.turning_speed * self.delta_time)
            self.direction.normalize()
        super().update()
        
class NaveBullet(Bullet):
    def __init__(self, img: str, side: int, tabs: List[int]):
        super().__init__(img, side, tabs)
        self.tags.append("player_projectile")
        self.speed = 600
        self.direction.y = -1
        
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
        
        self.speed : float = 0 # joga os rastrinho pra essa direcao sempre
        
        for i in range(rastros):
            rastro : Object = Object(
                "assets/images/rastro.png",
                int(self._width * i / rastros + 2),
                int(self._height * i / rastros + 2),
                tabs,
                2,
                z=1
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
            self.rastros[i].pos.x = self.rastros[i+1].get_center().x - self.rastros[i].get_width()/2
            self.rastros[i].pos.y = self.rastros[i+1].get_center().y - self.rastros[i].get_height()/2
            self.rastros[i].pos.y += self.speed * self.delta_time
    
    def render(self):
        return

class Nave(Body):
    
    rastro : Rastro
    
    def __init__(self, image: str, width: int, height: int, side: int, tabs: List[int], h_parts: int = 2):
        super().__init__(image, width, height, side, tabs, h_parts, z=1)
        self.tags.append("player")
        self.damage_from_tags = {"enemy_projectile", "asteroid"}
        self.keyboard = get_screen().keyboard
        self.speed : float = 250
        self.direction : Vector2 = Vector2(0,0)
        self.hitbox = DEFAULT_NAVE_HITBOX.copy()
        
        """Stats vars"""
        self.default_health : float = 5
        self.health : float = self.default_health
        self.score : int = 0
        # tempo ate poder levar dano de novo
        self.damage_interval : float = 1
        self.damage_cooldown : float = 0
        
        """Bullet vars"""
        self.bullet_img : str = "assets/images/bullet_white.png"
        self.bullet_explosion_img : str = "assets/images/explosion_small.png"
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
        self.bullet_instance_counter : List[int] = [0]
        # so pode atirar se quantidade de balas for menor que max_bullet_count
        self.max_bullet_count : int = -1 # se -1, pode atirar o quanto quiser
    
    def shoot(self):
        if self.max_bullet_count == -1 or self.bullet_instance_counter[0] < self.max_bullet_count:
            self.spawn_bullet()
            self.bullets[-1].horizontal_bounds = self.horizontal_bounds
            self.bullets[-1].side = self.side
            if self.anchor != self:
                self.bullets[-1].anchor = self.anchor
            self.bullets[-1].explosion_info["img"] = self.bullet_explosion_img
            self.bullets[-1].instance_counter = self.bullet_instance_counter
            self.bullet_instance_counter[0] += 1
    
    def spawn_bullet(self):
        self.bullets.append(NaveBullet(self.bullet_img, self.side, self.get_tabs()))
        self.bullets[-1].pos.x = self.pos.x + self.get_width()/2 - self.bullets[-1].get_width()/2
        self.bullets[-1].pos.y = self.pos.y - self.bullets[-1].get_height() + 5

    def spawn_rastro(self):
        self.rastro : Rastro = Rastro(self.get_tabs(), 8)
        self.rastro.speed = 400
        self.rastro.horizontal_bounds = self.horizontal_bounds
        if self.rastro.anchor != self:
            self.rastro.anchor = self.anchor
        for r in self.rastro.rastros:
            r.horizontal_bounds = self.horizontal_bounds
        self.apply_rastro_offset()
    
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
        for rastro in self.rastro.rastros:
            get_screen().remove_object_by_id(rastro.get_id())
        get_screen().remove_object_by_id(self.rastro.get_id())
    
    def check_damage(self):
        colliders = self.get_colliders(self.damage_from_tags)
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
        super().update()
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
        
        if self.anchor != self:
            anchor_movement = self.anchor.get_movement()
            for rastro in self.rastro.rastros:
                rastro.pos -= (anchor_movement) * self.offset_multiplier
        
        self.rastro.pos.x = self.pos.x
        self.rastro.pos.y = self.pos.y
        self.rastro.delta_time = self.delta_time
        self.rastro.update()
        
        
        
