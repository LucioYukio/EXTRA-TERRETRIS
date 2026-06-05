from typing import Dict

from pygame import image, Surface


images: Dict[str, Surface] = {
    "assets/images/explosion.png": image.load("assets/images/explosion.png").convert_alpha()
}

def get_image(filepath: str):
    """
    Checa de a imagem ja existe no cache.
    Se existe, retorna uma copia da surface respectiva.
    Se nao, adiciona no cache e retorna a surface.
    Isso eh necessario porque pesa muito pegar do disco toda vez.
    """
    img : Surface | None = images.get(filepath, None)
    
    if img == None:
        images[filepath] = image.load(filepath).convert_alpha()
        return images[filepath]
    else:
        return img