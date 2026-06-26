from typing import List

from engine.const import EMPTY_PIXEL
from engine.object import Object
from engine.vector2 import Vector2
from engine.screen import get_screen
from config import sounds
from entities.effect import Effect
from ui.text import Text

GRID_COLS = 3
GRID_ROWS = 2
NUM_SLOTS = 6

MOVE_COOLDOWN = 0.35
BUY_COOLDOWN = 0.5

LABEL_AREA_HEIGHT = 40
LABEL_PADDING = 2
CIRCLE_SIZE = 24

UP_IDX = 0
DOWN_IDX = 1
LEFT_IDX = 2
RIGHT_IDX = 3
BUY_IDX = 4
CONFIRM_IDX = 5

NAVE_PRICES = [20, 10, 40, 30, 20, 30]
TETRIS_PRICES = [25, 15, 10, 15, 15, 35]

NAVE_NAMES = ["Slow Enemy", "Heal", "Kill All", "Side Shot", "Speed Up", "Shield"]
TETRIS_NAMES = ["Block Bar", "Erase Line", "New Piece", "Slow Fall", "Enemy Fall", "Clear Grid"]

LABEL_SIZE = Vector2(12, 12)

CURSOR_IMAGES = [
    "assets/images/circle_purple.png",
    "assets/images/circle_green.png",
]


class _Cursor:
    def __init__(self):
        self.row: int = 0
        self.col: int = 0
        self.finished: bool = False
        self.move_cooldown: float = 0.0
        self.buy_cooldown: float = 0.0

    def reset(self):
        self.row = 0
        self.col = 0
        self.finished = False
        self.move_cooldown = 0.0
        self.buy_cooldown = 0.0

    @property
    def slot_index(self) -> int:
        return self.row * GRID_COLS + self.col


class PowerStore(Object):
    def __init__(self, powers_ref: List[List[int]], currency: List[int],
                 icon_image: str, total_frames: int,
                 icon_size: Vector2, gap: int, prices: List[int],
                 names: List[str],
                 tabs: List[int], control_schemes: List[List[str]]):
        grid_w = int(GRID_COLS * icon_size.x + (GRID_COLS - 1) * gap)
        grid_h = int(GRID_ROWS * icon_size.y + (GRID_ROWS - 1) * gap + LABEL_AREA_HEIGHT)
        super().__init__(EMPTY_PIXEL, grid_w, grid_h, tabs, 1)
        self.playing = False

        self.powers_ref = powers_ref
        self.currency = currency
        self.prices = prices
        self.control_schemes = control_schemes
        self.icon_size = icon_size
        self.gap = gap
        self.ready = False

        self.cursors = [_Cursor(), _Cursor()]

        self.slots: List[Object] = []
        self.name_labels: List[Text] = []
        self.price_labels: List[Text] = []
        self._build_slots(icon_image, total_frames, tabs, names, prices)

        self.circles: List[Object] = []
        self._build_cursors(tabs)

        self._update_cursor_positions()

    # --- grid building ---

    def _build_slots(self, icon_image: str, total_frames: int,
                     tabs: List[int], names: List[str], prices: List[int]):
        for slot_index in range(NUM_SLOTS):
            row = slot_index // GRID_COLS
            col = slot_index % GRID_COLS
            icon = self._make_slot_icon(icon_image, total_frames, tabs, slot_index, row, col)
            self.slots.append(icon)

            name_label = self._make_name_label(names[slot_index], tabs, icon)
            self.name_labels.append(name_label)

            price_label = self._make_price_label(prices[slot_index], tabs, name_label)
            self.price_labels.append(price_label)

    def _make_slot_icon(self, icon_image: str, total_frames: int,
                        tabs: List[int], slot_index: int,
                        row: int, col: int) -> Object:
        icon = Object(icon_image, int(self.icon_size.x), int(self.icon_size.y), tabs, 1)
        icon.set_total_frames(total_frames)
        icon.set_curr_frame(slot_index)
        icon.playing = False
        icon.pos.x = col * (self.icon_size.x + self.gap)
        icon.pos.y = row * (self.icon_size.y + self.gap)
        return icon

    def _make_name_label(self, name: str, tabs: List[int], icon: Object) -> Text:
        label = Text(name, LABEL_SIZE, tabs, color_index=1)
        label.pos.x = icon.pos.x
        label.pos.y = icon.pos.y + self.icon_size.y + LABEL_PADDING
        return label

    def _make_price_label(self, price: int, tabs: List[int], name_label: Text) -> Text:
        label = Text(str(price), LABEL_SIZE, tabs, color_index=1)
        label.pos.x = name_label.pos.x
        label.pos.y = name_label.pos.y + LABEL_SIZE.y + LABEL_PADDING
        return label

    def _build_cursors(self, tabs: List[int]):
        for side in range(2):
            circle = Object(CURSOR_IMAGES[side], CIRCLE_SIZE, CIRCLE_SIZE, tabs, 2)
            circle.playing = False
            self.circles.append(circle)

    # --- cursor positioning ---

    def _update_cursor_positions(self):
        for side in range(2):
            cursor = self.cursors[side]
            slot = self.slots[cursor.slot_index]
            if side == 0:
                self.circles[side].pos.x = slot.pos.x - CIRCLE_SIZE / 2
            else:
                self.circles[side].pos.x = slot.pos.x + slot.get_width() - CIRCLE_SIZE / 2
            self.circles[side].pos.y = slot.pos.y - CIRCLE_SIZE / 2

    # --- slot label positioning ---

    def _position_slot_and_labels(self, slot_index: int, icon: Object):
        row = slot_index // GRID_COLS
        col = slot_index % GRID_COLS
        icon.pos.x = self.pos.x + col * (self.icon_size.x + self.gap)
        icon.pos.y = self.pos.y + row * (self.icon_size.y + self.gap)
        self.name_labels[slot_index].pos.x = icon.pos.x
        self.name_labels[slot_index].pos.y = icon.pos.y + self.icon_size.y + LABEL_PADDING
        self.price_labels[slot_index].pos.x = icon.pos.x
        self.price_labels[slot_index].pos.y = self.name_labels[slot_index].pos.y + LABEL_SIZE.y + LABEL_PADDING

    # --- per-player input ---

    @staticmethod
    def _clamp_row(row: int) -> int:
        return max(0, min(GRID_ROWS - 1, row))

    @staticmethod
    def _clamp_col(col: int) -> int:
        return max(0, min(GRID_COLS - 1, col))

    def _handle_cursor_movement(self, cursor: _Cursor, keys: list, keyboard) -> bool:
        if cursor.move_cooldown > 0:
            return False
        moved = False
        if keyboard.key_pressed(keys[UP_IDX]):
            cursor.row = self._clamp_row(cursor.row - 1)
            moved = True
        elif keyboard.key_pressed(keys[DOWN_IDX]):
            cursor.row = self._clamp_row(cursor.row + 1)
            moved = True
        if keyboard.key_pressed(keys[LEFT_IDX]):
            cursor.col = self._clamp_col(cursor.col - 1)
            moved = True
        elif keyboard.key_pressed(keys[RIGHT_IDX]):
            cursor.col = self._clamp_col(cursor.col + 1)
            moved = True
        if moved:
            cursor.move_cooldown = MOVE_COOLDOWN
        return moved

    def _handle_buy(self, cursor: _Cursor, side: int, keys: list, keyboard):
        if cursor.buy_cooldown > 0:
            return
        if not keyboard.key_pressed(keys[BUY_IDX]):
            return
        price = self.prices[cursor.slot_index]
        if self.currency[side] >= price:
            self.currency[side] -= price
            self.powers_ref[side].append(cursor.slot_index)
            sounds.BOUGHT.play()
            cursor.buy_cooldown = BUY_COOLDOWN
            # efeitinho de compra
            fx = Effect(
                f"assets/images/bought_{'purple' if side == 0 else 'green'}.png",
                30, 0.2, CIRCLE_SIZE, CIRCLE_SIZE*2, self.get_tabs(), 1
            )
            fx.pos.x = self.circles[side].get_center().x - fx.get_width()//2
            fx.pos.y = self.circles[side].pos.y - fx.get_height()

    def _handle_confirm(self, cursor: _Cursor, keys: list, keyboard):
        if keyboard.key_pressed(keys[CONFIRM_IDX]):
            cursor.finished = True

    def _handle_player_input(self, side: int) -> bool:
        cursor = self.cursors[side]
        if cursor.finished:
            return True

        delta = self.delta_time
        cursor.move_cooldown = max(cursor.move_cooldown - delta, 0)
        cursor.buy_cooldown = max(cursor.buy_cooldown - delta, 0)

        keys = self.control_schemes[side]
        keyboard = get_screen().keyboard

        self._handle_cursor_movement(cursor, keys, keyboard)
        self._handle_buy(cursor, side, keys, keyboard)
        self._handle_confirm(cursor, keys, keyboard)

        return False

    def update(self):
        super().update()

        for slot_index, icon in enumerate(self.slots):
            self._position_slot_and_labels(slot_index, icon)

        all_finished = True
        for side in range(2):
            finished = self._handle_player_input(side)
            all_finished = all_finished and finished

        self._update_cursor_positions()

        if all_finished:
            self.ready = True

    def reset(self):
        for cursor in self.cursors:
            cursor.reset()
        self.ready = False

    def destroy(self):
        super().destroy()
        for label in self.name_labels:
            label.wants_to_die = True
        for label in self.price_labels:
            label.wants_to_die = True


class NavePowerStore(PowerStore):
    def __init__(self, powers_ref: List[List[int]], currency: List[int],
                 tabs: List[int], control_schemes: List[List[str]],
                 icon_size: Vector2 = Vector2(128, 128), gap: int = 18):
        super().__init__(
            powers_ref, currency,
            "assets/images/powers_nave.png", 10,
            icon_size, gap, NAVE_PRICES, NAVE_NAMES,
            tabs, control_schemes,
        )


class TetrisPowerStore(PowerStore):
    def __init__(self, powers_ref: List[List[int]], currency: List[int],
                 tabs: List[int], control_schemes: List[List[str]],
                 icon_size: Vector2 = Vector2(128, 128), gap: int = 18):
        super().__init__(
            powers_ref, currency,
            "assets/images/powers_tetris.png", 10,
            icon_size, gap, TETRIS_PRICES, TETRIS_NAMES,
            tabs, control_schemes,
        )
