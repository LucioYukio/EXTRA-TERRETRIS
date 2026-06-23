from typing import Dict, Tuple

from pygame import image, Surface, transform


_cache: Dict[Tuple[str, int, int], Surface] = {}

def get_image(filepath: str, width: int = 0, height: int = 0):
    key = (filepath, width, height)
    cached = _cache.get(key)
    if cached is not None:
        return cached

    if width == 0 and height == 0:
        _cache[key] = image.load(filepath).convert_alpha()
        return _cache[key]

    original_key = (filepath, 0, 0)
    original = _cache.get(original_key)
    if original is None:
        original = image.load(filepath).convert_alpha()
        _cache[original_key] = original

    scaled = transform.scale(original, (width, height))
    _cache[key] = scaled
    return scaled
