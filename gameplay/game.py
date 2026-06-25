from copy import copy
from random import choice, randrange, uniform
from typing import List, Tuple

from config import sounds
from config import tabs
from config.preload import preload_images
from engine.const import REF_RES, clamp, get_screen
from engine.object import Object
from engine.vector2 import Vector2
from entities.bullets import Bullet
from entities.enemy import Enemy, EnemyBullet, EnemySin, FollowingEnemyBullet, SpinEnemy
from entities.fades import WhiteFadeIn, WhiteFadeOut, BlackFadeIn, BlackFadeOut
from entities.nave import DEFAULT_ENEMY_SIZE, DEFAULT_NAVE_SIZE, Nave
from entities import powers
from tetris.tetris import Tetris
from ui.text import Text

from .config import (
    ENEMY_POOL,
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

        self.enemy_spawn_interval = 5 / self.difficulty_mult
        self.enemy_spawn_cooldown = 5 / self.difficulty_mult

        preload_images()
        setup_tab_backgrounds()

        self.naves: Tuple[Nave, Nave] = setup_naves()
        self.bgs_far, self.bgs = setup_backgrounds(self.naves)
        self.asteroids = setup_asteroids(self.naves, self.difficulty_mult, self.auras)

        from .config import TETRIS_LINES
        piece_size = Vector2(REF_RES[1] / TETRIS_LINES, REF_RES[1] / TETRIS_LINES)
        self.tetris: Tuple[Tetris, Tetris] = setup_tetris(piece_size)

        (self.tetris_power_stacks,
         self.nave_power_stacks) = setup_power_stacks(self.tetris, self.naves)

        self.nave_store, self.tetris_store = setup_stores(self.naves, self.tetris, self.auras)

        (self.sidepanels, self.points_texts, self.aura_text,
         self.aura_text_values, self.alien_displays, self.lose_screens,
         self.win_screens, self.divisao) = setup_ui_elements(self.naves)

        for fade_cls in (WhiteFadeIn, WhiteFadeOut, BlackFadeIn, BlackFadeOut):
            fade = fade_cls([tabs.NAVE], total_duration=0.016)
            fade.visible = False

    # ---- helpers ----

    def get_random_pos(self, side: int) -> int:
        return randrange(REF_RES[0] // 2 * side, REF_RES[0] // 2 * (side + 1)) if side == 0 else randrange(REF_RES[0] // 2, REF_RES[0])

    def reset_enemy(self, enemy: Enemy):
        enemy.pos.x = self.get_random_pos(enemy.side)
        enemy.pos.y = -enemy.get_height() + 1
        enemy.health = enemy.default_health

    def spawn_enemy(self, x: float, side: int):
        img = "assets/images/nave_inimiga_verde.png" if side == 0 else "assets/images/nave_inimiga_roxa.png"
        
        # escolher inimigo da enemy pool
        inimigo : Enemy | None = None
        enemy_type = choice(ENEMY_POOL)
        match enemy_type:
            case "EnemySin":
                inimigo = EnemySin(
                    int(DEFAULT_ENEMY_SIZE.x),
                    int(DEFAULT_ENEMY_SIZE.y),
                    side,
                    self.naves[side],
                    [tabs.NAVE])
            case "SpinEnemy":
                inimigo = SpinEnemy(
                    int(DEFAULT_ENEMY_SIZE.x),
                    int(DEFAULT_ENEMY_SIZE.x),
                    side,
                    self.naves[side],
                    [tabs.NAVE]
                )
            case _:
                inimigo = Enemy(
                    int(DEFAULT_ENEMY_SIZE.x),
                    int(DEFAULT_ENEMY_SIZE.y),
                    side,
                    self.naves[side],
                    [tabs.NAVE])
        
        if not inimigo: return
        
        inimigo.instance_counter = self.enemy_counter
        self.enemy_counter[0] += 1
        inimigo.bullet_instance_counter = self.enemy_bullet_counter
        inimigo.max_bullet_count = MAX_ENEMY_BULLET_COUNT

        x = clamp(x, 0, REF_RES[0] - inimigo.get_width())
        inimigo.pos.x = x
        inimigo.pos.y = -inimigo.get_height() + 1
        inimigo.horizontal_bounds = copy(H_BOUNDS[side])
        inimigo.anchor = self.naves[side]
        inimigo.vertical_bounds = Vector2(-inimigo.get_height(), REF_RES[1] + inimigo.get_height())
        inimigo.bullet_img = "assets/images/bullet_green.png" if side == 0 else "assets/images/bullet_purple.png"
        inimigo.bullet_explosion_img = "assets/images/explosion_small_green.png" if side == 0 else "assets/images/explosion_small_purple.png"
        inimigo.side = side
        inimigo.points_list = self.auras
        inimigo.speed *= self.difficulty_mult
        inimigo.shooting_interval = 1 / self.difficulty_mult
        inimigo.bullet_speed_mult = self.difficulty_mult

    # ---- reset ----

    def reset_game(self):
        self.round_over = False
        for t in self.tetris:
            t.reset()
            t.enabled = True
        for nave in self.naves:
            nave.health = nave.default_health
            nave.wants_to_die = False
            nave.dead = False
            nave.enabled = True
            nave.damage_cooldown = 0
            nave.shooting_cooldown = 0
            nave.power_cooldown = nave.power_interval
            nave.blinking = False
            nave.visible = True
            nave.pressing_both = Vector2(0, 0)
            for bullet in nave.bullets:
                bullet.wants_to_die = True
            nave.bullets.clear()
        self.naves[0].pos.x = REF_RES[0] / 4 - self.naves[0].get_width() / 2
        self.naves[0].pos.y = REF_RES[1] - self.naves[0].get_height() - 8
        self.naves[1].pos.x = REF_RES[0] / 4 + REF_RES[0] / 2 - self.naves[1].get_width() / 2
        self.naves[1].pos.y = REF_RES[1] - self.naves[1].get_height() - 8
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
        sounds.HEAL_NAVE.play()
        self.naves[side].health += amount

    def increase_speed(self, side: int):
        if not self.speed_increased[side]:
            self.naves[side].speed *= NAVE_SPEED_INCREASE
            self.speed_increased[side] = True

    def decrease_enemy_speed(self, side: int):
        sounds.SLOW_DOWN.play()
        if not self.enemy_speed_decreased[side]:
            self.naves[1 - side].speed *= ENEMY_SPEED_DECREASE
            self.enemy_speed_decreased[side] = True

    def side_shoot(self, side: int):
        sounds.SIDE_SHOT.play()
        b: Bullet = FollowingEnemyBullet(
            "assets/images/bullet_red.png", 1 - side, [tabs.NAVE],
            self.naves[1 - side], 0.01,
        )
        b.direction = Vector2(1 - side, 0)
        b.pos = self.naves[side].pos.copy()
        b.set_width(48)
        b.set_height(48)
        b.z = 3
        b.horizontal_bounds = Vector2(-1, -1)

    def kill_all(self, side: int):
        sounds.KILL_ALL.play()
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
        self.naves[side].shake(30, 1)

    def shield_up(self, side: int):
        sounds.SHIELD_NAVE.play()
        self.naves[side].damage_cooldown = SHIELD_UP_DURATION
        self.naves[side].activate_shield()

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
        sounds.BLOCKED_BAR.play()
        self.tetris[1 - side].add_blocked_line_bellow()

    def erase_bottom(self, side: int):
        sounds.ERASE_BOTTOM.play()
        target = self.tetris[side]
        for i in range(target.lines - 1, -1, -1):
            row = target.matrix[i]
            if any(t != 0 for t in row):
                target.matrix.pop(i)
                target.matrix.insert(0, [0] * target.columns)
                break

    def new_piece(self, side: int):
        sounds.NEW_PIECE.play()
        self.tetris[side].choice_piece()

    def increase_enemy_gravity(self, side: int):
        if not self.tetris_gravity_increased[side]:
            self.tetris[1 - side].gravity_speed *= TETRIS_GRAVITY_INCREASE
            self.tetris_gravity_increased[side] = True

    def decrease_your_gravity(self, side: int):
        sounds.SLOW_DOWN.play()
        if not self.tetris_gravity_decreased[side]:
            self.tetris[side].gravity_speed *= TETRIS_GRAVITY_DECREASE
            self.tetris_gravity_decreased[side] = True

    def clear_grid(self, side: int):
        sounds.KILL_ALL.play()
        self.tetris[side].build_matrix()
        fade = WhiteFadeOut(
            [tabs.TETRIS], 0.2,
            int(REF_RES[0] / 2 - SIDEPANEL_W - DIVISOR_W / 2),
            REF_RES[1],
        )
        fade.pos.x = SIDEPANEL_W if side == 0 else int(REF_RES[0] / 2 + DIVISOR_W / 2)

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
            # ---- NAVE tab (always handle deaths to prevent removal from screen) ----
            if screen.get_tab() == tabs.NAVE:
                for side in (0, 1):
                    nave = self.naves[side]
                    other = self.naves[1 - side]
                    if nave.wants_to_die and not nave.dead:
                        if not self.round_over:
                            self.auras[1 - side] += int(other.health * AURA_REWARD_MULTIPLIER)
                            self.lose_screens[side].show(3)
                            self.win_screens[1 - side].show(3)
                            self.round_over = True
                            self.switch_cooldown = 3
                            self.switch_target = tabs.TETRIS_LOJA
                            sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                            sounds.SABOTAGE_INCOMING.play()
                            self.points[1 - side] += 1
                        nave.dead = True
                        nave.enabled = False

            # ---- NAVE tab (active gameplay) ----
            if screen.get_tab() == tabs.NAVE and self.switch_cooldown <= 0:
                if self.enemy_spawn_cooldown <= 0 and self.enemy_counter[0] + 2 <= MAX_ENEMY_COUNT:
                    self.spawn_enemy(self.get_random_pos(0), 0)
                    self.spawn_enemy(self.get_random_pos(1), 1)
                    self.enemy_spawn_cooldown = self.enemy_spawn_interval + uniform(-0.5, 0.5)

                for o in screen._objs:
                    if o.pos.y >= REF_RES[1] and isinstance(o, Enemy):
                        self.reset_enemy(o)

                for side in (0, 1):
                    nave = self.naves[side]
                    other = self.naves[1 - side]

                    if nave.damage_cooldown > 0:
                        self.alien_displays[side].hurt()
                        if self.speed_increased[1 - side]:
                            other.speed /= NAVE_SPEED_INCREASE
                            self.speed_increased[1 - side] = False
                        if self.enemy_speed_decreased[side]:
                            other.speed /= ENEMY_SPEED_DECREASE
                            self.enemy_speed_decreased[side] = False

                    if nave.wants_to_power:
                        power = nave.pop_power()
                        self.nave_use_power(power, side)
                        nave.wants_to_power = False

                self.bgs[0].pos.y += BG_VELOCITY
                if self.bgs[0].pos.y >= -self.bgs[0].get_height() / 3:
                    self.bgs[0].pos.y -= self.bgs[0].get_height() / 3
                self.bgs[1].pos.y += BG_VELOCITY
                if self.bgs[1].pos.y >= -self.bgs[1].get_height() / 3:
                    self.bgs[1].pos.y -= self.bgs[1].get_height() / 3
                for asteroid in self.asteroids:
                    if asteroid.pos.y >= REF_RES[1]:
                        asteroid.pos.y = REF_RES[1] * 2
                    if asteroid.reset_timer >= ASTEROID_RESET_INTERVAL:
                        asteroid.pos.y = -asteroid.get_height()
                        asteroid.pos.x = self.get_random_pos(asteroid.side)

            # ---- TETRIS tab ----
            if screen.get_tab() == tabs.TETRIS and self.switch_cooldown <= 0:
                for side in (0, 1):
                    t = self.tetris[side]
                    t.pos.x = ((SIDEPANEL_W + REF_RES[0] / 2 - DIVISOR_W / 2) / 2 - t.get_width() / 2) if side == 0 else ((REF_RES[0] / 2 + DIVISOR_W / 2 + REF_RES[0] - SIDEPANEL_W) / 2 - t.get_width() / 2)

                for side in (0, 1):
                    if self.tetris[side].check_loss():
                        self.auras[1 - side] += int(self.naves[1 - side].health * AURA_REWARD_MULTIPLIER)
                        self.lose_screens[side].show(3)
                        self.win_screens[1 - side].show(3)
                        for t in self.tetris:
                            t.enabled = False
                        self.switch_cooldown = 3
                        self.switch_target = tabs.NAVE_LOJA
                        sounds.MUSICA.set_volume(sounds.MUSICA.volume / 1.5)
                        sounds.ROUND_END.play()
                        self.points[1 - side] += 1

                for side in (0, 1):
                    t = self.tetris[side]
                    if t.wants_to_power:
                        power = t.pop_power()
                        self.tetris_use_power(power, side)
                        t.wants_to_power = False

                for side in (0, 1):
                    t = self.tetris[side]
                    if t.points > 0:
                        self.auras[side] += t.points * TETRIS_POINTS_MULTIPLIER
                        t.points = 0

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
            self.aura_text_values[0].value = self.auras[0]
            self.aura_text_values[1].value = self.auras[1]

            self.points_texts[0].value = self.points[0]
            self.points_texts[1].value = self.points[1]

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
