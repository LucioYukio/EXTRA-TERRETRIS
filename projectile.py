from body import Body
from screen import Vector2, List
class Projectile(Body):
    def __init__(self, image: str, width: int, height: int, side: int, tabs: List[int], h_parts: int = 1):
        super().__init__(image, width, height, side, tabs, h_parts)
        self.keep_in_bounds = False
        self.destroy_out_of_h_bounds = True
        self.destroy_out_of_v_bounds = True
        self.damage : float = 1
        # destruir se sair da tela
        self.destroy_out_of_screen : bool = True
        self.destroy_on_hit : bool = True
        self.wants_to_die : bool = False
        self.tags.append("projectile")
        
        self.direction : Vector2 = Vector2()
        self.speed : float = 1
        
        self.categorie = "projectile"
    
    def get_damage(self):
        return self.damage
    
    def update(self):
        self.direction.normalize()
        self.velocity = self.direction * self.speed
        super().update()
        