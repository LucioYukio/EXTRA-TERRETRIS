from typing import List

from engine.const import EMPTY_PIXEL
from engine.object import Object
from engine.vector2 import Vector2
from engine.screen import get_screen
from config import sounds
from ui.text import Text

GRID_COLS = 3
GRID_ROWS = 2
NUM_SLOTS = 6
MOVE_COOLDOWN = 0.35
BUY_COOLDOWN = 0.5

NAVE_PRICES = [20, 10, 40, 30, 20, 30]
TETRIS_PRICES = [25, 15, 10, 15, 15, 35]

NAVE_NAMES = ["Slow Enemy", "Heal", "Kill All", "Side Shot", "Speed Up", "Shield"]
TETRIS_NAMES = ["Block Bar", "Erase Line", "New Piece", "Slow Fall", "Enemy Fall", "Clear Grid"]

LABEL_SIZE = Vector2(12, 12)


class PowerStore(Object):
    def __init__(self, powers_ref: List[List[int]], currency: List[int],
                 icon_image: str, total_frames: int,
                 icon_size: Vector2, gap: int, prices: List[int],
                 names: List[str],
                 tabs: List[int], control_schemes: List[List[str]]):
        width = int(GRID_COLS * icon_size.x + (GRID_COLS - 1) * gap)
        height = int(GRID_ROWS * icon_size.y + (GRID_ROWS - 1) * gap + 40)
        super().__init__(EMPTY_PIXEL, width, height, tabs, 1)
        self.playing = False

        self.powers_ref = powers_ref
        self.currency = currency
        self.prices = prices
        self.control_schemes = control_schemes
        self.icon_size = icon_size
        self.gap = gap
        self.ready = False

        self.cursors = [
            {"row": 0, "col": 0, "finished": False, "move_cd": 0.0, "buy_cd": 0.0},
            {"row": 0, "col": 0, "finished": False, "move_cd": 0.0, "buy_cd": 0.0},
        ]

        self.slots: List[Object] = []
        self.name_labels: List[Text] = []
        self.price_labels: List[Text] = []
        for i in range(NUM_SLOTS):
            row = i // GRID_COLS
            col = i % GRID_COLS
            icon = Object(icon_image, int(icon_size.x), int(icon_size.y), tabs, 1)
            icon.set_total_frames(total_frames)
            icon.set_curr_frame(i)
            icon.playing = False
            icon.pos.x = col * (icon_size.x + gap)
            icon.pos.y = row * (icon_size.y + gap)
            self.slots.append(icon)

            name_label = Text(names[i], LABEL_SIZE, tabs, color_index=1)
            name_label.pos.x = icon.pos.x
            name_label.pos.y = icon.pos.y + icon_size.y + 2
            self.name_labels.append(name_label)

            price_label = Text(str(prices[i]), LABEL_SIZE, tabs, color_index=1)
            price_label.pos.x = icon.pos.x
            price_label.pos.y = name_label.pos.y + LABEL_SIZE.y + 2
            self.price_labels.append(price_label)

        self.circle_imgs = ["assets/images/circle_purple.png", "assets/images/circle_green.png"]
        self.circle_size = 24
        self.circles: List[Object] = []
        for p in range(2):
            circle = Object(self.circle_imgs[p], self.circle_size, self.circle_size, tabs, 2)
            circle.playing = False
            self.circles.append(circle)

        self.update_cursor_positions()

    def update_cursor_positions(self):
        for p in range(2):
            slot_idx = self.cursors[p]["row"] * GRID_COLS + self.cursors[p]["col"]
            slot = self.slots[slot_idx]
            if p == 0:
                self.circles[p].pos.x = slot.pos.x - self.circle_size / 2
            else:
                self.circles[p].pos.x = slot.pos.x + slot.get_width() - self.circle_size / 2
            self.circles[p].pos.y = slot.pos.y - self.circle_size / 2

    def update(self):
        super().update()
        dt = self.delta_time

        for i, icon in enumerate(self.slots):
            row = i // GRID_COLS
            col = i % GRID_COLS
            icon.pos.x = self.pos.x + col * (self.icon_size.x + self.gap)
            icon.pos.y = self.pos.y + row * (self.icon_size.y + self.gap)
            self.name_labels[i].pos.x = icon.pos.x
            self.name_labels[i].pos.y = icon.pos.y + self.icon_size.y + 2
            self.price_labels[i].pos.x = icon.pos.x
            self.price_labels[i].pos.y = self.name_labels[i].pos.y + LABEL_SIZE.y + 2

        all_finished = True

        for p in range(2):
            c = self.cursors[p]
            if c["finished"]:
                continue

            all_finished = False
            c["move_cd"] = max(c["move_cd"] - dt, 0)
            c["buy_cd"] = max(c["buy_cd"] - dt, 0)
            scheme = self.control_schemes[p]
            kb = get_screen().keyboard

            if c["move_cd"] <= 0:
                moved = False
                if kb.key_pressed(scheme[0]):
                    c["row"] = max(0, c["row"] - 1)
                    moved = True
                elif kb.key_pressed(scheme[1]):
                    c["row"] = min(GRID_ROWS - 1, c["row"] + 1)
                    moved = True
                if kb.key_pressed(scheme[2]):
                    c["col"] = max(0, c["col"] - 1)
                    moved = True
                elif kb.key_pressed(scheme[3]):
                    c["col"] = min(GRID_COLS - 1, c["col"] + 1)
                    moved = True
                if moved:
                    c["move_cd"] = MOVE_COOLDOWN

            if c["buy_cd"] <= 0 and kb.key_pressed(scheme[4]):
                slot_idx = c["row"] * GRID_COLS + c["col"]
                price = self.prices[slot_idx]
                if self.currency[p] >= price:
                    self.currency[p] -= price
                    self.powers_ref[p].append(slot_idx)
                    sounds.BOUGHT.play()
                c["buy_cd"] = BUY_COOLDOWN

            if kb.key_pressed(scheme[5]):
                c["finished"] = True

        self.update_cursor_positions()

        if all_finished:
            self.ready = True

    def reset(self):
        for c in self.cursors:
            c["row"] = 0
            c["col"] = 0
            c["finished"] = False
            c["move_cd"] = 0.0
            c["buy_cd"] = 0.0
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
