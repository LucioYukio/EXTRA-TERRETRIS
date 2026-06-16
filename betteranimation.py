from imagecache import get_image
from pplay import animation as a

class Animation(a.Animation):
    def __init__(self, filepath: str, total_frames: int = 1):
        super().__init__("assets/images/empty_pixel.png", total_frames)
        self.image = get_image(filepath)
        self.img_filepath = filepath