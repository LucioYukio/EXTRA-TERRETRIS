from typing import Dict, List

from config.sounds import TIRO, ACERTO
from entities.effect import Effect
from entities.projectile import Projectile
from engine.object import Object
from engine.screen import get_screen
from engine.vector2 import Vector2


class Bullet(Projectile):
    def __init__(self, img: str, side: int, tabs: List[int]):
        super().__init__(img, 18, 18, side, tabs)
        self.set_total_frames(4)
        self.frame_duration = 0.1

        self.destroy_out_of_h_bounds = False

        self.explosion_info: Dict = {
            "img": "assets/images/explosion_small.png",
            "frames": 8,
            "duration": 0.2,
            "width": 48,
            "height": 48
        }

        self.categorie = "bullet"

        TIRO.stop()
        TIRO.play()

    def update(self):
        super().update()

    def spawn_explosion(self):
        explosion = Effect(
            self.explosion_info["img"],
            self.explosion_info["frames"],
            self.explosion_info["duration"],
            self.explosion_info["width"],
            self.explosion_info["height"],
            self.get_tabs()
        )

        target_coords = self.get_center()
        target_coords.x -= explosion.get_width() / 2
        target_coords.y -= explosion.get_height() / 2

        explosion.pos.x = target_coords.x
        explosion.pos.y = target_coords.y

        ACERTO.stop()
        ACERTO.play()


class FollowingBullet(Bullet):
    def __init__(self, img: str, side: int, target: Object, turning_speed: float, tabs: List[int]):
        super().__init__(img, side, tabs)
        self.target = target
        self.turning_speed = turning_speed
        self.following_duration = 0.5

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
