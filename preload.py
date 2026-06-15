from screen import get_image

HEAVY_IMAGES = [
    "assets/images/double_bg.png",
    "assets/images/asteroids_bg_narrow.png",
    "assets/images/asteroids_bg_narrow_close.png",
    "assets/images/tech_background_green_animated.png",
    "assets/images/tech_background_purple_animated.png",
    "assets/images/sidepanel_background_green.png",
    "assets/images/sidepanel_background_purple.png",
    "assets/images/explosion.png",
    "assets/images/spinning_asteroid.png",
    "assets/images/nave1.png",
    "assets/images/nave2.png",
    "assets/images/letters_black_and_white.png",
    "assets/images/white_fade_in.png",
    "assets/images/white_fade_out.png",
    "assets/images/black_fade_in.png",
    "assets/images/black_fade_out.png",
]

def preload_images():
    for path in HEAVY_IMAGES:
        get_image(path)
