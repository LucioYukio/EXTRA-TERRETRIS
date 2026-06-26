from typing import List

from entities.body import Body
from entities.bullets import Bullet, NaveBullet
from engine.const import EMPTY_PIXEL
from engine.object import Object
from engine.screen import get_screen
from engine.vector2 import Vector2

DEFAULT_NAVE_SIZE = Vector2(69, 83)
DEFAULT_NAVE_HITBOX = Vector2(20, 30)

DEFAULT_ENEMY_SIZE = Vector2(86, 83)


class Rastro(Object):
    def __init__(self, tabs: List[int], rastros: int):
        super().__init__(EMPTY_PIXEL, 8, 8, tabs)

        self.rastros: List[Object] = []
        self.qtd = rastros

        self.offset = Vector2(0, 0)

        self.interval = 0.15
        self.cooldown = 0

        self.destroy_out_of_h_bounds = False
        self.destroy_out_of_v_bounds = False
        self.keep_in_bounds = False

        self.speed = 0

        for i in range(rastros):
            rastro = Object(
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

    def advance_rastro(self):
        if self.qtd <= 0:
            return

        self.rastros[-1].pos.x = self.pos.x + self.offset.x - self._width / 2
        self.rastros[-1].pos.y = self.pos.y + self.offset.y - self._height + 1
        for i in range(self.qtd - 1):
            self.rastros[i].pos.x = self.rastros[i + 1].get_center().x - self.rastros[i].get_width() / 2
            self.rastros[i].pos.y = self.rastros[i + 1].get_center().y - self.rastros[i].get_height() / 2
            self.rastros[i].pos.y += self.speed * self.delta_time

    def render(self):
        return


class Nave(Body):
    rastro: Rastro

    def __init__(self, image: str, width: int, height: int, side: int, tabs: List[int], h_parts: int = 2):
        super().__init__(image, width, height, side, tabs, h_parts, z=1)
        self.tags.append("player")
        self.damage_from_tags = {"enemy_projectile", "asteroid", "debri"}
        self.keyboard = get_screen().keyboard
        self.speed : float = 200
        self.direction = Vector2(0, 0)
        self.hitbox = DEFAULT_NAVE_HITBOX.copy()

        self.default_health = 5
        self.health = self.default_health
        self.score = 0
        self.damage_interval = 1
        self.damage_cooldown = 0

        self.blinking = False
        self.blinking_interval = 0.1
        self.blinking_cooldown = 0

        self.bullet_img = "assets/images/bullet_white.png"
        self.bullet_explosion_img = "assets/images/explosion_small.png"
        self.default_shooting_interval = 0.2
        self.shooting_interval = self.default_shooting_interval
        self.shooting_cooldown = 0
        self.bullets: List[Bullet] = []

        self.UP = "up"
        self.DOWN = "down"
        self.LEFT = "left"
        self.RIGHT = "right"
        self.SHOOT = "space"
        self.POWER = "x"
        self.pressing_both = Vector2(0, 0)

        self.categorie = "nave"
        self.bullet_instance_counter: List[int] = [0]
        self.max_bullet_count = -1

        shield_size = int(max(width, height))
        self.shield = Object("assets/images/shield.png", shield_size, shield_size, tabs, 1, z=2)
        self.shield.set_total_frames(4)
        self.shield.frame_duration = 0.01
        self.shield.visible = False
        
        self.powers : List[int] = []
        self.power_interval : float = 1
        self.power_cooldown : float = self.power_interval
        self.wants_to_power : bool = False # if this nave wants to use a power

    def shoot(self):
        if self.max_bullet_count == -1 or self.bullet_instance_counter[0] < self.max_bullet_count:
            self.spawn_bullet()
            self.bullets[-1].horizontal_bounds = self.horizontal_bounds
            self.bullets[-1].side = self.side
            self.bullets[-1].anchor = self.anchor
            self.bullets[-1].explosion_info["img"] = self.bullet_explosion_img
            self.bullets[-1].instance_counter = self.bullet_instance_counter
            self.bullet_instance_counter[0] += 1

    def spawn_bullet(self):
        self.bullets.append(NaveBullet(self.bullet_img, self.side, self.get_tabs()))
        self.bullets[-1].pos.x = self.pos.x + self.get_width() / 2 - self.bullets[-1].get_width() / 2
        self.bullets[-1].pos.y = self.pos.y - self.bullets[-1].get_height() + 5

    def spawn_rastro(self):
        self.rastro = Rastro(self.get_tabs(), 4)
        self.rastro.speed = 400
        self.rastro.horizontal_bounds = self.horizontal_bounds
        if self.rastro.anchor != self:
            self.rastro.anchor = self.anchor
        for r in self.rastro.rastros:
            r.horizontal_bounds = self.horizontal_bounds
        self.apply_rastro_offset()

    def apply_rastro_offset(self):
        try:
            self.rastro
        except AttributeError:
            self.spawn_rastro()
        self.rastro.offset = Vector2(self.get_width() / 2, self.get_height())

    def set_height(self, height: float):
        super().set_height(height)
        self.apply_rastro_offset()

    def set_width(self, width: float):
        super().set_width(width)
        self.apply_rastro_offset()

    def add_power(self, power: int):
        self.powers.append(power)
    
    def pop_power(self):
        return self.powers.pop(0)
    
    def get_direction(self):
        direction_x = self.keyboard.key_pressed(self.RIGHT) - self.keyboard.key_pressed(self.LEFT)
        if self.keyboard.key_pressed(self.RIGHT) and self.keyboard.key_pressed(self.LEFT):
            if self.pressing_both.x == 0:
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

    def check_power(self):
        if self.keyboard.key_pressed(self.POWER) and self.power_cooldown <= 0 and self.powers:
            self.wants_to_power = True
            self.power_cooldown = self.power_interval

    def destroy_rastro(self):
        if not hasattr(self, "rastro"):
            return
        self.rastro.wants_to_die = True

    def destroy(self):
        super().destroy()
        for rastro in self.rastro.rastros:
            get_screen().remove_object_by_id(rastro.get_id())
        get_screen().remove_object_by_id(self.rastro.get_id())
        self.shield.wants_to_die = True

    def activate_shield(self):
        self.shield.visible = True

    def deactivate_shield(self):
        self.shield.visible = False

    def check_damage(self):
        if self.damage_cooldown > 0:
            return
        colliders = self.get_colliders(self.damage_from_tags)
        for c in colliders:
            from entities.projectile import Projectile
            if isinstance(c, Projectile):
                if self.damage_from_tags and not any(tag in c.tags for tag in self.damage_from_tags):
                    continue
                if c in self.bullets:
                    continue
                self.health -= c.get_damage()
                self.damage_cooldown = self.damage_interval
                self.shake(c.get_damage() * 5, 0.5)
                c.wants_to_die = c.destroy_on_hit
                if c.destroy_on_hit and isinstance(c, Bullet):
                    c.spawn_explosion()
        if self.health <= 0:
            self.spawn_explosion()
            self.wants_to_die = True

    def update_rastro_pos(self):
        self.rastro.pos.x = self.pos.x
        self.rastro.pos.y = self.pos.y

    def destroy_bullet(self, bullet: Bullet):
        bullet.wants_to_die = True
        self.bullets.remove(bullet)

    def propagate_bounds(self):
        self.rastro.horizontal_bounds = self.horizontal_bounds
        self.rastro.propagate_bounds()

    def update(self):
        if not self.enabled:
            return
        super().update()
        if self.rastro.horizontal_bounds != self.horizontal_bounds:
            self.propagate_bounds()

        self.get_direction()

        self.direction.normalize()
        self.velocity.x = self.direction.x * self.speed
        self.velocity.y = self.direction.y * self.speed

        self.check_shoot()
        self.check_power()
        self.check_damage()

        for b in self.bullets:
            if b.wants_to_die or (b.destroy_out_of_screen and b.out_of_screen):
                self.destroy_bullet(b)

        self.shooting_cooldown = max(self.shooting_cooldown - self.delta_time, 0)
        
        self.power_cooldown = max(self.power_cooldown - self.delta_time, 0)

        if self.anchor != self:
            anchor_movement = self.anchor.get_movement()
            for rastro in self.rastro.rastros:
                rastro.pos -= (anchor_movement) * self.offset_multiplier

        if self.damage_cooldown > 0:
            if self.blinking_cooldown <= 0:
                self.blinking_cooldown = self.blinking_interval
                self.blinking = not self.blinking
            else:
                self.blinking_cooldown -= self.delta_time
            self.visible = self.blinking

            self.damage_cooldown -= self.delta_time
        else:
            self.visible = True
            self.deactivate_shield()

        self.rastro.delta_time = self.delta_time
        self.rastro.update()

        self.shield.pos.x = self.pos.x + (self.get_width() - self.shield.get_width()) / 2
        self.shield.pos.y = self.pos.y + (self.get_height() - self.shield.get_height()) / 2

        self.update_rastro_pos()