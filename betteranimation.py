from typing import Dict
from pplay import animation as a
from pygame import Surface, image

images: Dict[str, Surface] = {}
def get_image(filepath: str):
    img : Surface | None = images.get(filepath, None)
    if img == None:
        images[filepath] = image.load(filepath).convert_alpha()
        return images[filepath]
    else:
        return img

class Animation(a.Animation):
    def __init__(self, filepath: str, total_frames: int = 1):
        super().__init__("assets/images/empty_pixel.png", total_frames)
        self.image = get_image(filepath)
        self.img_filepath = filepath # guarda o caminho se quiser usar depois