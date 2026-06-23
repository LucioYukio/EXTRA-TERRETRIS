from typing import List

from entities.effect import Effect
from engine.const import REF_RES


class Fade(Effect):
    def __init__(self, image: str, tabs: List[int], total_duration: float = 1, width: int = REF_RES[0], height: int = REF_RES[1]):
        super().__init__(image, 16, total_duration, width, height, tabs, h_parts=1)
        self.z = 100


class WhiteFadeIn(Fade):
    def __init__(self, tabs: List[int], total_duration: float = 1, width: int = REF_RES[0], height: int = REF_RES[1]):
        super().__init__("assets/images/white_fade_in.png", tabs, total_duration, width=width, height=height)


class WhiteFadeOut(Fade):
    def __init__(self, tabs: List[int], total_duration: float = 1, width: int = REF_RES[0], height: int = REF_RES[1]):
        super().__init__("assets/images/white_fade_out.png", tabs, total_duration, width=width, height=height)


class BlackFadeIn(Fade):
    def __init__(self, tabs: List[int], total_duration: float = 1, width: int = REF_RES[0], height: int = REF_RES[1]):
        super().__init__("assets/images/black_fade_in.png", tabs, total_duration, width=width, height=height)


class BlackFadeOut(Fade):
    def __init__(self, tabs: List[int], total_duration: float = 1, width: int = REF_RES[0], height: int = REF_RES[1]):
        super().__init__("assets/images/black_fade_out.png", tabs, total_duration, width=width, height=height)
