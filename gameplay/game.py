from copy import copy
from random import randrange, uniform
from typing import List

from config import sounds
from config import tabs
from config.preload import preload_images
from engine.const import REF_RES, clamp, get_screen
from engine.object import Object
from engine.vector2 import Vector2
from entities.enemy import Enemy, EnemyBullet, EnemySin
from entities.fades import WhiteFadeIn, WhiteFadeOut, BlackFadeIn, BlackFadeOut
from entities.nave import DEFAULT_NAVE_SIZE
from entities import powers
from ui.text import Text

from .config import (
    SIDEPANEL_W,
    DIVISOR_W,
    H_BOUNDS,
    DEFAULT_LETTER_SIZE,
    SMALL_LETTER_SIZE,
    BG_VELOCITY,
    ASTEROID_RESET_INTERVAL,
    TETRIS_POINTS_MULTIPLIER,
    AURA_REWARD_MULTIPLIER,
    NAVE_SPEED_INCREASE,
    ENEMY_SPEED_DECREASE,
    SHIELD_UP_DURATION,
    TETRIS_GRAVITY_INCREASE,
    TETRIS_GRAVITY_DECREASE,
    MAX_ENEMY_COUNT,
    MAX_ENEMY_BULLET_COUNT,
)
from .setup import (
    setup_tab_backgrounds,
    setup_naves,
    setup_backgrounds,
    setup_asteroids,
    setup_tetris,
    setup_power_stacks,
    setup_stores,
    setup_ui_elements,
)


class Game:
    def __init__(self, difficulty: str, win_points: int):
        self.difficulty_mult = {"lento": 0.5, "normal": 1, "frenetico": 3}.get(difficulty, 1)
        self.win_points = win_points

        self.auras: List[int] = [0, 0]
        self.points: List[int] = [0, 0]
        self.enemy_counter: List[int] = [0]
        self.enemy_bullet_counter: List[int] = [0]
        self.round_over = False

        self.speed_increased = [False, False]
        self.enemy_speed_decreased = [False, False]
        self.tetris_gravity_increased = [False, False]
        self.tetris_gravity_decreased = [False, False]

        self.wants_to_quit = False
        self.switch_cooldown = 0.0
        self.switch_target = -1

        self.enemy_spawn_interval = 2 / self.difficulty_mult
        self.enemy_spawn_cooldown = 5 / self.difficulty_mult

        preload_images()
        setup_tab_backgrounds()

        self.nave1, self.nave2 = setup_naves()
        self.bg_far1, self.bg1, self.bg_far2, self.bg2 = setup_backgrounds(
            self.nave1, self.nave2
        )
        self.asteroids = setup_asteroids(
            self.nave1, self.nave2, self.difficulty_mult, self.auras
        )

        from .config import TETRIS_LINES
        piece_size = Vector2(REF_RES[1] / TETRIS_LINES, REF_RES[1] / TETRIS_LINES)
        self.tetris1, self.tetris2 = setup_tetris(piece_size)

        (self.tetris_powers1, self.tetris_powers2,
         self.nave_powers1, self.nave_powers2) = setup_power_stacks(
            self.tetris1, self.tetris2, self.nave1, self.nave2,
        )

        self.nave_store, self.tetris_store = setup_stores(
            self.nave1, self.nave2, self.tetris1, self.tetris2, self.auras,
        )

        ui = setup_ui_elements(self.nave1, self.nave2)
        self.sidepanel1 = ui["sidepanel1"]
        self.sidepanel2 = ui["sidepanel2"]
        self.points_text1 = ui["points_text1"]
        self.points_text2 = ui["points_text2"]
        self.aura_text = ui["aura_text"]
        self.aura1_text_value = ui["aura1_text_value"]
        self.aura2_text_value = ui["aura2_text_value"]
        self.purple_alien_display = ui["purple_alien_display"]
        self.green_alien_display = ui["green_alien_display"]
        self.lose_screens = ui["lose_screens"]
        self.win_screens = ui["win_screens"]
        self.divisao = ui["divisao"]

        for fade_cls in (WhiteFadeIn, WhiteFadeOut, BlackFadeIn, BlackFadeOut):
            fade = fade_cls([tabs.NAVE], total_duration=0.016)
            fade.visible = False

    # ---- helpers ----

    def get_random_pos(self, side: int) -> int:
        if side == 0:
            return randrange(0, REF_RES[0] // 2)
        else:
            return randrange(REF_RES[0] // 2, REF_RES[0])

    def reset_enemy(self, enemy: Enemy):
        enemy.pos.x = self.get_random_pos(enemy.side)
        enemy.pos.y = -enemy.get_height() + 1
        enemy.health = enemy.default_health

    def spawn_enemy(self, x: float, side: int):
        img = "assets/images/nave_inimiga_verde.png" if side == 0 else "assets/images/nave_inimiga_roxa.png"
        inimigo = EnemySin(
            img,
            int(DEFAULT_NAVE_SIZE.x),
            int(DEFAULT_NAVE_SIZE.y),
            side,
            self.nave1 if side == 0 else self.nave2,
            [tabs.NAVE],
        )
        inimigo.instance_counter = self.enemy_counter
        self.enemy_counter[0] += 1
        inimigo.bullet_instance_counter = self.enemy_bullet_counter
        inimigo.max_bullet_count = MAX_ENEMY_BULLET_COUNT

        x = clamp(x, 0, REF_RES[0] - inimigo.get_width())
        inimigo.pos.x = x
        inimigo.pos.y = -inimigo.get_height() + 1
        inimigo.horizontal_bounds = copy(H_BOUNDS[side])
        if side == 0:
            inimigo.anchor = self.nave1
        else:
            inimigo.anchor = self.nave2
        inimigo.vertical_bounds = Vector2(-inimigo.get_height(), REF_RES[1] + inimigo.get_height())
        inimigo.bullet_img = "assets/images/bullet_green.png" if side == 0 else "assets/images/bullet_purple.png"
        inimigo.bullet_explosion_img = "assets/images/explosion_small_green.png" if side == 0 else "assets/images/explosion_small_purple.png"
        inimigo.side = side
        inimigo.points_list = self.auras
        inimigo.speed = 200 * self.difficulty_mult
        inimigo.shooting_interval = 1 / self.difficulty_mult
        inimigo.bullet_speed_mult = self.difficulty_mult

    # ---- reset ----

    def reset_game(self):
        self.round_over = False
        self.tetris1.reset()
        self.tetris2.reset()
        self.tetris1.enabled = True
        self.tetris2.enabled = True
        for nave in (self.nave1, self.nave2):
            nave.health = nave.default_health
            nave.wants_to_die = False
            nave.dead = False
            nave.enabled = True
            nave.damage_cooldown = 0
            nave.shooting_cooldown = 0
            nave.blinking = False
            nave.visible = True
            nave.pressing_both = Vector2(0, 0)
            for bullet in nave.bullets:
                bullet.wants_to_die = True
            nave.bullets.clear()
        self.nave1.pos.x = REF_RES[0] / 4 - self.nave1.get_width() / 2
        self.nave1.pos.y = REF_RES[1] - self.nave1.get_height() - 8
        self.nave2.pos.x = REF_RES[0] / 4 + REF_RES[0] / 2 - self.nave2.get_width() / 2
        self.nave2.pos.y = REF_RES[1] - self.nave2.get_height() - 8
        for obj in get_screen()._objs:
            if isinstance(obj, Enemy):
                self.reset_enemy(obj)
            elif obj.categorie in ("bullet", "nave bullet", "debri", "projectile"):
                obj.wants_to_die = True
        for asteroid in self.asteroids:
            asteroid.pos.y = REF_RES[1] * 2
            asteroid.health = asteroid.total_health
        self.enemy_spawn_cooldown = 5 / self.difficulty_mult

    # ---- nave power effects ----

    def heal(self, side: int, amount: int = 1):
        if side == 0:
            self.nave1.health += amount
        else:
            self.nave2.health += amount

    def increase_speed(self, side: int):
        if side == 0:
            if not self.speed_increased[0]:
                self.nave1.speed *= NAVE_SPEED_INCREASE
                self.speed_increased[0] = True
        else:
            if not self.speed_increased[1]:
                self.nave2.speed *= NAVE_SPEED_INCREASE
                self.speed_increased[1] = True

    def decrease_enemy_speed(self, side: int):
        if side == 0:
            if not self.enemy_speed_decreased[0]:
                self.nave2.speed *= ENEMY_SPEED_DECREASE
                self.enemy_speed_decreased[0] = True
        else:
            if not self.enemy_speed_decreased[1]:
                self.nave1.speed *= ENEMY_SPEED_DECREASE
                self.enemy_speed_decreased[1] = True

    def side_shoot(self, side: int):
        b: EnemyBullet = EnemyBullet(
            "assets/images/bullet_red.png", 1 - side, [tabs.NAVE],
            self.nave1 if side else self.nave2, 0.01,
        )
        b.direction = Vector2(1 - side, 0)
        b.pos = self.nave1.pos.copy() if side == 0 else self.nave2.pos.copy()
        b.set_width(48)
        b.set_height(48)
        b.z = 6
        b.horizontal_bounds = Vector2(-1, -1)

    def kill_all(self, side: int):
        for obj in get_screen().get_objs_in_tab(tabs.NAVE):
            if isinstance(obj, Enemy) and obj.side == side:
                obj.wants_to_die = True
            if isinstance(obj, EnemyBullet) and obj.side == side:
                obj.wants_to_die = True
        fade = WhiteFadeOut(
            [tabs.NAVE], 0.2,
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
        )
        fade.pos.x = SIDEPANEL_W if side == 0 else int(REF_RES[0] / 2 + DIVISOR_W / 2)

    def shield_up(self, side: int):
        if side == 0:
            self.nave1.damage_cooldown = SHIELD_UP_DURATION
            self.nave1.activate_shield()
        else:
            self.nave2.damage_cooldown = SHIELD_UP_DURATION
            self.nave2.activate_shield()

    def nave_use_power(self, power: int, side: int):
        match power:
            case powers.DECREASE_ENEMY_SPEED: self.decrease_enemy_speed(side)
            case powers.HEAL: self.heal(side)
            case powers.KILL_ALL: self.kill_all(side)
            case powers.SIDE_SHOT: self.side_shoot(side)
            case powers.INCREASE_SPEED: self.increase_speed(side)
            case powers.SHIELD_UP: self.shield_up(side)

    # ---- tetris power effects ----

    def add_blocked_bar(self, side: int):
        if side == 0:
            self.tetris2.add_blocked_line_bellow()
        else:
            self.tetris1.add_blocked_line_bellow()

    def erase_bottom(self, side: int):
        target = self.tetris1 if side == 0 else self.tetris2
        for i in range(target.lines - 1, -1, -1):
            row = target.matrix[i]
            if any(t != 0 for t in row):
                target.matrix.pop(i)
                target.matrix.insert(0, [0] * target.columns)
                break

    def new_piece(self, side: int):
        if side == 0:
            self.tetris1.choice_piece()
        else:
            self.tetris2.choice_piece()

    def increase_enemy_gravity(self, side: int):
        if side == 0:
            if not self.tetris_gravity_increased[0]:
                self.tetris2.gravity_speed *= TETRIS_GRAVITY_INCREASE
                self.tetris_gravity_increased[0] = True
        else:
            if not self.tetris_gravity_increased[1]:
                self.tetris1.gravity_speed *= TETRIS_GRAVITY_INCREASE
                self.tetris_gravity_increased[1] = True

    def decrease_your_gravity(self, side: int):
        if side == 0:
            if not self.tetris_gravity_decreased[0]:
                self.tetris1.gravity_speed *= TETRIS_GRAVITY_DECREASE
                self.tetris_gravity_decreased[0] = True
        else:
            if not self.tetris_gravity_decreased[1]:
                self.tetris2.gravity_speed *= TETRIS_GRAVITY_DECREASE
                self.tetris_gravity_decreased[1] = True

    def clear_grid(self, side: int):
        if side == 0:
            self.tetris1.build_matrix()
        else:
            self.tetris2.build_matrix()

    def tetris_use_power(self, power: int, side: int):
        match power:
            case powers.BLOCKED_BAR: self.add_blocked_bar(side)
            case powers.ERASE_BOTTOM: self.erase_bottom(side)
            case powers.NEW_PIECE: self.new_piece(side)
            case powers.DECREASE_GRAVITY: self.decrease_your_gravity(side)
            case powers.INCREASE_ENEMY_GRAVITY: self.increase_enemy_gravity(side)
            case powers.CLEAR_GRID: self.clear_grid(side)

    # ---- main loop ----

    def run(self):
        screen = get_screen()
        screen.set_tab(tabs.NAVE)

        sounds.MUSICA.loop = True
        sounds.MUSICA.set_volume(20)
        sounds.MUSICA.stop()
        sounds.MUSICA.play()

        while not self.wants_to_quit:
            if self.switch_cooldown <= 0:
                if screen.keyboard.key_pressed("t"):
                    screen.set_tab(tabs.TETRIS)
                if screen.keyboard.key_pressed("j"):
                    screen.set_tab(tabs.NAVE)

            # ---- NAVE tab ----
            if screen.get_tab() == tabs.NAVE and self.switch_cooldown <= 0:
                if self.enemy_spawn_cooldown <= 0 and self.enemy_counter[0] + 2 <= MAX_ENEMY_COUNT:
                    self.spawn_enemy(self.get_random_pos(0), 0)
                    self.spawn_enemy(self.get_random_pos(1), 1)
                    self.enemy_spawn_cooldown = self.enemy_spawn_interval + uniform(-0.5, 0.5)

                for o in screen._objs:
                    if o.pos.y >= REF_RES[1] and isinstance(o, Enemy):
                        self.reset_enemy(o)

                if self.nave1.damage_cooldown > 0:
                    self.purple_alien_display.hurt()
                    if self.speed_increased[1]:
                        self.nave2.speed /= NAVE_SPEED_INCREASE
                        self.speed_increased[1] = False
                    if self.enemy_speed_decreased[0]:
                        self.nave2.speed /= ENEMY_SPEED_DECREASE
                        self.enemy_speed_decreased[0] = False

                if self.nave2.damage_cooldown > 0:
                    self.green_alien_display.hurt()
                    if self.speed_increased[0]:
                        self.nave1.speed /= NAVE_SPEED_INCREASE
                        self.speed_increased[0] = False
                    if self.enemy_speed_decreased[1]:
                        self.nave1.speed /= ENEMY_SPEED_DECREASE
                        self.enemy_speed_decreased[1] = False

                if self.nave1.wants_to_power:
                    power = self.nave1.pop_power()
                    self.nave_use_power(power, 0)
                    self.nave1.wants_to_power = False

                if self.nave1.wants_to_die and not self.nave1.dead and not self.round_over:
                    self.auras[1] += int(self.nave2.health * AURA_REWARD_MULTIPLIER)
                    self.lose_screens[0].show(3)
                    self.win_screens[1].show(3)
                    self.nave1.dead = True
                    self.nave1.enabled = False
                    self.round_over = True
                    self.switch_cooldown = 3
                    self.switch_target = tabs.TETRIS_LOJA
                    sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                    sounds.SABOTAGE_INCOMING.play()
                    self.points[1] += 1

                if self.nave2.wants_to_power:
                    power = self.nave2.pop_power()
                    self.nave_use_power(power, 1)
                    self.nave2.wants_to_power = False

                if self.nave2.wants_to_die and not self.nave2.dead and not self.round_over:
                    self.auras[0] += int(self.nave1.health * AURA_REWARD_MULTIPLIER)
                    self.lose_screens[1].show(3)
                    self.win_screens[0].show(3)
                    self.nave2.dead = True
                    self.nave2.enabled = False
                    self.round_over = True
                    self.switch_cooldown = 3
                    self.switch_target = tabs.TETRIS_LOJA
                    sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                    sounds.SABOTAGE_INCOMING.play()
                    self.points[0] += 1

                self.bg1.pos.y += BG_VELOCITY
                if self.bg1.pos.y >= -self.bg1.get_height() / 3:
                    self.bg1.pos.y -= self.bg1.get_height() / 3
                self.bg2.pos.y += BG_VELOCITY
                if self.bg2.pos.y >= -self.bg2.get_height() / 3:
                    self.bg2.pos.y -= self.bg2.get_height() / 3
                for asteroid in self.asteroids:
                    if asteroid.pos.y >= REF_RES[1]:
                        asteroid.pos.y = REF_RES[1] * 2
                    if asteroid.reset_timer >= ASTEROID_RESET_INTERVAL:
                        asteroid.pos.y = -asteroid.get_height()
                        asteroid.pos.x = self.get_random_pos(asteroid.side)

            # ---- TETRIS tab ----
            if screen.get_tab() == tabs.TETRIS and self.switch_cooldown <= 0:
                self.tetris1.pos.x = (SIDEPANEL_W + REF_RES[0] / 2 - DIVISOR_W / 2) / 2 - self.tetris1.get_width() / 2
                self.tetris2.pos.x = (REF_RES[0] / 2 + DIVISOR_W / 2 + REF_RES[0] - SIDEPANEL_W) / 2 - self.tetris2.get_width() / 2

                if self.tetris1.check_loss():
                    self.auras[1] += int(self.nave2.health * AURA_REWARD_MULTIPLIER)
                    self.lose_screens[0].show(3)
                    self.win_screens[1].show(3)
                    self.tetris1.enabled = False
                    self.tetris2.enabled = False
                    self.switch_cooldown = 3
                    self.switch_target = tabs.NAVE_LOJA
                    sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                    sounds.ROUND_END.play()
                    self.points[1] += 1
                if self.tetris2.check_loss():
                    self.auras[0] += int(self.nave1.health * AURA_REWARD_MULTIPLIER)
                    self.lose_screens[1].show(3)
                    self.win_screens[0].show(3)
                    self.tetris1.enabled = False
                    self.tetris2.enabled = False
                    self.switch_cooldown = 3
                    self.switch_target = tabs.NAVE_LOJA
                    sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                    sounds.ROUND_END.play()
                    self.points[0] += 1

                if self.tetris1.wants_to_power:
                    power = self.tetris1.pop_power()
                    self.tetris_use_power(power, 0)
                    self.tetris1.wants_to_power = False

                if self.tetris2.wants_to_power:
                    power = self.tetris2.pop_power()
                    self.tetris_use_power(power, 1)
                    self.tetris2.wants_to_power = False

                if self.tetris1.points > 0:
                    self.auras[0] += self.tetris1.points * TETRIS_POINTS_MULTIPLIER
                    self.tetris1.points = 0
                if self.tetris2.points > 0:
                    self.auras[1] += self.tetris2.points * TETRIS_POINTS_MULTIPLIER
                    self.tetris2.points = 0

            # ---- TETRIS_LOJA tab ----
            if screen.get_tab() == tabs.TETRIS_LOJA and self.switch_cooldown <= 0:
                self.tetris_store.pos.x = REF_RES[0] / 2 - self.tetris_store.get_width() / 2
                self.tetris_store.pos.y = REF_RES[1] / 2 - self.tetris_store.get_height() / 2
                self.tetris_store.update()
                if self.tetris_store.ready:
                    self.reset_game()
                    screen.set_tab(tabs.TETRIS)
                    self.tetris_store.reset()
                    self.enemy_spawn_cooldown = 5 / self.difficulty_mult

            # ---- NAVE_LOJA tab ----
            if screen.get_tab() == tabs.NAVE_LOJA and self.switch_cooldown <= 0:
                self.nave_store.pos.x = REF_RES[0] / 2 - self.nave_store.get_width() / 2
                self.nave_store.pos.y = REF_RES[1] / 2 - self.nave_store.get_height() / 2
                self.nave_store.update()
                if self.nave_store.ready:
                    self.reset_game()
                    screen.set_tab(tabs.NAVE)
                    self.nave_store.reset()
                    self.enemy_spawn_cooldown = 5 / self.difficulty_mult

            # ---- common updates ----
            self.enemy_spawn_cooldown = max(
                self.enemy_spawn_cooldown - screen.window.delta_time(), 0
            )

            self.aura_text.pos.x = REF_RES[0] / 2 - self.aura_text.get_width() / 2
            self.aura_text.pos.y = REF_RES[1] - self.aura_text.get_height()
            self.aura1_text_value.value = self.auras[0]
            self.aura2_text_value.value = self.auras[1]

            self.points_text1.value = self.points[0]
            self.points_text2.value = self.points[1]

            if self.switch_cooldown > 0:
                self.switch_cooldown -= screen.window.delta_time()
                if self.switch_cooldown <= 0 and self.switch_target >= 0:
                    self.reset_game()
                    if self.points[0] >= self.win_points or self.points[1] >= self.win_points:
                        self._show_win_screen()
                    else:
                        screen.set_tab(self.switch_target)
                        self.switch_target = -1
                        sounds.MUSICA.set_volume(sounds.MUSICA.volume * 1.5)

            if screen.keyboard.key_pressed("esc"):
                self.wants_to_quit = True

            screen.update()

    def _show_win_screen(self):
        screen = get_screen()
        winner = 0 if self.points[0] >= self.win_points else 1
        winner_name = "Purple" if winner == 0 else "Green"
        alien_img = "assets/images/alien_purple_idle.png" if winner == 0 else "assets/images/alien_green_idle.png"

        Object("assets/images/black_pixel.png", REF_RES[0], REF_RES[1], [tabs.WIN], 0)

        win_text = Text(f"{winner_name} dominou toda a galaxia!", DEFAULT_LETTER_SIZE, [tabs.WIN], color_index=1)
        win_text.pos.x = int(REF_RES[0] / 2 - win_text.get_width() / 2)
        win_text.pos.y = int(REF_RES[1] / 2 - 200)

        alien = Object(alien_img, 200, 250, [tabs.WIN], 1)
        alien.set_total_frames(67 if winner == 1 else 40)
        alien.frame_duration = 0.05
        alien.pos.x = int(REF_RES[0] / 2 - alien.get_width() / 2)
        alien.pos.y = int(REF_RES[1] / 2 - 50)

        esc_text = Text("Press ESC to return", SMALL_LETTER_SIZE, [tabs.WIN], color_index=1)
        esc_text.pos.x = int(REF_RES[0] / 2 - esc_text.get_width() / 2)
        esc_text.pos.y = int(REF_RES[1] - 100)

        self.switch_target = -1
        screen.set_tab(tabs.WIN)

        while not screen.keyboard.key_pressed("esc"):
            screen.update()

        screen.clear_tab(tabs.WIN)
        self.wants_to_quit = True
