from body import *
from pplay.animation import Animation
class Projectile(Body):
    def __init__(self, image: str, width: int, height: int, tab: int, objs: list, h_parts: int = 1):
        super().__init__(image, width, height, tab, objs, h_parts)
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = True
        self.destroy_out_of_v_bounds = True
        self.damage : float = 1
        # destruir se sair da tela
        self.destroy_out_of_screen : bool = True
        self.destroy_on_hit : bool = True
        self.wants_to_die : bool = False
        self.tags.append("projectile")
        
        self.categorie = "projectile"
    
    def get_damage(self):
        return self.damage