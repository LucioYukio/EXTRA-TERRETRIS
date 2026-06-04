# usar cada tab como se fosse uma janela
# da pra trocar de tab facilmente
# as tabs tem um offset muito grande e sao desenhadas so quando selecionadas
import math
from typing import List, Tuple

import pplay.window as w
import pplay.gameobject as go
import pplay.gameimage as gi
import pplay.animation as a
import pplay.keyboard as k
import pplay.mouse as m
import pplay.gameobject as go
import pplay.window as w
import pygame.transform
from mouse import Mouse
from vector2 import Vector2

# TODO make a global delta_time and time elapsed variables

REF_RES = (1600, 900) # tamanhos seram calculados em relacao a essa variavel
res_scale : List[float] = [1,1]

TELA_W = 1600
TELA_H = 900

EMPTY_PIXEL = "assets/images/empty_pixel.png"

def update_res_scale(new_res : List[float]):
    global REF_RES, res_scale
    res_scale[0] = new_res[0]/REF_RES[0]
    res_scale[1] = new_res[1]/REF_RES[1]


def clamp(x, min, max):
    if x < min:
        return min
    if x > max:
        return max
    return x

def pt_to_px(pt: float):
    return pt*1.333

def get_text_size(text: str, font_name: str, size_pt: int):
    """retorna o tamanho do texto em pixels"""
    if not pygame.font.get_init():
        pygame.font.init()
    font = pygame.font.SysFont(font_name, size_pt)
    return font.size(text)

class Object:
    _width : int = 0
    _height : int = 0
    ## se diferente de -1, considera esse valor como limites verticais
    horizontal_bounds : Vector2 = Vector2(-1, -1)
    ## se diferente de -1, considera esse valor como limites verticais
    vertical_bounds : Vector2 = Vector2(-1, -1)
    ## precisa ser atualizado pela screen antes do update
    out_of_h_bounds : bool = False
    ## precisa ser atualizado pela screen antes do update
    out_of_v_bounds : bool = False
    def __init__(self, image : str, width : int, height: int, tabs: List[int], h_parts : int = 1, add_to_screen: bool = True):
        self._mouse : Mouse = get_screen().mouse
        self._keyboard : k.Keyboard = get_screen().keyboard

        self.image : str = image
        self.sprites : List[a.Animation] = []
        # how many horizontal parts the object has, used for rendering
        self.h_parts : int = h_parts

        """tab da qual o objeto pertence"""
        self._tabs : List[int] = tabs

        """Coordenadas locais"""
        self.pos : Vector2 = Vector2()
        # posicao no ultimo frame
        self.last_pos : Vector2 = Vector2()
        self.z : int = 0 # ordem de desenho; camada; maior valor eh desenhado na frente
        # multiplica os offsets contabilizados no apply_coords()
        self.offset_multiplier : float = 0 # quanto maior, mais perto da tela. Quanto mais proximo de 0, mais longe.
        # offset sera calculado em relacao a esse objeto.
        self.anchor : Object = self

        """Tamanho local"""
        self.set_width(width)
        self.set_height(height)

        """variaveis de animacao"""
        self.frame_duration : float = 1 # em segundos, maior que 0
        self.total_frames : int = 1

        self.build_sprites()

        self.visible : bool = True
        self.enabled : bool = True
        self.playing : bool = True
        self.delta_time : float = 0
        self.time_elapsed : float = 0
        ## precisa ser atualizado pela screen antes do update
        self.out_of_screen : bool = False
        ## se diferente de -1, considera esse valor como limites horizontais
        self.horizontal_bounds : Vector2 = Vector2(-1, -1)
        ## se diferente de -1, considera esse valor como limites verticais
        self.vertical_bounds : Vector2 = Vector2(-1, -1)
        ## precisa ser atualizado pela screen antes do update
        self.out_of_h_bounds : bool = False
        ## precisa ser atualizado pela screen antes do update
        self.out_of_v_bounds : bool = False
        ## precisa ser atualizado pela screen antes do update
        self.screen_size : Vector2 = Vector2(1600, 900)
        self.keep_in_bounds : bool = True

        self.destroy_out_of_h_bounds : bool = False
        self.destroy_out_of_v_bounds : bool = False
        self.categorie : str = ""

        self.tags = []

        self._id     : int      = 0
        
        self.wants_to_die : bool = False

        if add_to_screen:
            get_screen().add_object(self)

    def get_tabs(self):
        return self._tabs

    def add_tab(self, tab: int):
        self._tabs.append(tab)

    def remove_tab(self, tab: int):
        self._tabs.remove(tab)

    def get_id(self):
        return self._id

    def set_id(self, id: int):
        self._id = id

    def get_width(self):
        return self._width

    def set_width(self, width: float):
        self._width = int(width * res_scale[0])
        self.update_sprites()

    def get_height(self):
        return self._height

    def set_height(self, height: float):
        self._height = int(height * res_scale[1])
        self.update_sprites()

    def set_total_frames(self, total_frames: int):
        self.total_frames = total_frames
        self.playing = True
        self.build_sprites()

    def get_center(self):
        return Vector2(self.pos.x + self.get_width()/2, self.pos.y + self.get_height()/2)

    def build_sprites(self):
        self.sprites.clear()
        for i in range(self.h_parts):
            spr = a.Animation(self.image, self.total_frames)
            spr.playing = False
            self.sprites.append(spr)
        if self.image != EMPTY_PIXEL:
            self.update_sprites()
    
    def get_h_bounds(self):
        h_bounds : List[float] = []
        
        if self.horizontal_bounds.x != -1:
            h_bounds.append(self.horizontal_bounds.x)
        else:
            h_bounds.append(0)
        
        if self.horizontal_bounds.y != -1:
            h_bounds.append(self.horizontal_bounds.y)
        else:
            h_bounds.append(self.screen_size.x)
        
        return h_bounds

    def get_v_bounds(self):
        v_bounds : List[float] = []
        
        if self.vertical_bounds.x != -1:
            v_bounds.append(self.vertical_bounds.x)
        else:
            v_bounds.append(0)
        
        if self.vertical_bounds.y != -1:
            v_bounds.append(self.vertical_bounds.y)
        else:
            v_bounds.append(self.screen_size.x)
        
        return v_bounds
    
    # checks to see if the part is inside h_bounds
    def is_h_part_in_bounds(self, h_part : int):
        if self.out_of_h_bounds:
            return False
        coords : Vector2 = Vector2(
            self.pos.x + (self.get_width()/self.h_parts) * h_part,
            self.pos.y
        )
        size : Vector2 = Vector2(
            self.get_width()/self.h_parts,
            self.get_height()
        )
        
        h_bounds = self.get_h_bounds()
        
        if coords.x > h_bounds[1] - 1 or coords.x + size.x < h_bounds[0] + 1:
            return False
        return True

    def get_movement(self):
        """
        retorna movimento desse objeto no ultimo frame
        """
        return Vector2(
            self.pos.x - self.last_pos.x,
            self.pos.y - self.last_pos.y
        )

    def apply_coords(self, offset_x : float, offset_y : float):
        last_x : float = self.pos.x
        for i in range(self.h_parts):
            sprite = self.sprites[i]
            sprite.x = last_x
            sprite.y = self.pos.y
            last_x = sprite.x + sprite.width

    def animate(self):
        """Aplica a logica de animacao. Chamar em todo update."""
        if self.playing:
            curr_frame : int = int(self.time_elapsed / self.frame_duration) % self.total_frames
            for i in range(self.h_parts):
                spr = self.sprites[i]
                target_frame : int = i + (self.h_parts * curr_frame)
                if spr.curr_frame != target_frame:
                    spr.set_curr_frame(target_frame)

    def render(self):
        # check what sprites in this object are in bounds and render them.
        if not self.visible:
            return
        for i in range(self.h_parts):
            if self.is_h_part_in_bounds(i):
                self.sprites[i].draw()

    def update_sprites(self, grow_a_bit: bool = False):
        """
        Mudar o tamanho das imagens de acordo com o
        width e height
            grow_a_bit: if to make each part a little larger
        """
        # TODO corrigir pedacinho da direita nao aparecendo
        i : int = 0
        for spr in self.sprites:
            width = self.get_width() * self.total_frames
            #width = (self.get_width() + self.h_parts * grow_a_bit) * self.total_frames
            spr.image = pygame.transform.scale(spr.image, (width, self.get_height()))
            spr.width = int(self.get_width()/self.h_parts)
            #spr.width += 1
            spr.height = int(self.get_height())
            spr.curr_frame = i
            i += 1

    def update(self):
        self.last_pos.x = self.pos.x
        self.last_pos.y = self.pos.y
        
        self.delta_time = get_screen().window.delta_time()
        self.time_elapsed += self.delta_time
        
        self.screen_size.x = REF_RES[0] * res_scale[0]
        self.screen_size.y = REF_RES[1] * res_scale[1]
        
        if self.total_frames == 1 and self.playing == True:
            self.playing = False
        
        self.animate()
        for spr in self.sprites:
            spr.update()
        
        if self.anchor != self:
            anchor_movement = self.anchor.get_movement()
            self.pos.x -= anchor_movement.x * self.offset_multiplier
            self.pos.y -= anchor_movement.y * self.offset_multiplier
        
    # call this before "destroying" the object, for custom behaviour
    def destroy(self):
        pass

    def is_hovered(self):
        if get_screen().get_tab() not in self.get_tabs():
            return False
        
        mouse_pos = Vector2()
        mouse_pos.x, mouse_pos.y = self._mouse.get_position()
        
        if mouse_pos.x >= self.pos.x and mouse_pos.x <= self.pos.x + self.get_width() and\
            mouse_pos.y >= self.pos.y and mouse_pos.y <= self.pos.y + self.get_height():
                return True
        return False

    def is_pressed(self, button: int = 1):
        return self.is_hovered() and self._mouse.is_button_pressed(button)

    def is_just_pressed(self, button: int = 1):
        return self.is_hovered() and self._mouse.is_button_just_pressed(button)
    
class Screen:
    global res_scale
    def __init__(self, width : int, height : int):
        self.window      : w.Window     = w.Window(width, height)
        self._objs       : List         = []
        self._tab        : int          = 0
        self.bg_image    : str          = ""
        self._id_counter : int          = 0
        self.mouse       : Mouse        = Mouse()
        self.keyboard    : k.Keyboard   = k.Keyboard()
        # one color per tab
        self.bg_colors = {}
        # one image per tab
        self.bg_imgs = {}
        
        self.bg : gi.GameImage = gi.GameImage(EMPTY_PIXEL)
        
        self.ticks : int = 0
        self.time_elapsed : float = 0
        
        self.set_tab(0)
        

    def set_tab(self, tab: int):
        self._tab = tab
        self.set_bg_image()
    
    def get_tab(self):
        return self._tab
    
    def set_bg_image(self):
        if self.bg_imgs.get(self._tab):
            self.bg.image = pygame.transform.scale(gi.GameImage(self.bg_imgs[self._tab]).image, (self.window.width, self.window.height))

    def set_title(self, title: str):
        self.window.set_title(title)

    def add_object(self, obj : Object):
        obj.set_id(self._id_counter)
        self._id_counter += 1
        self._objs.append(obj)
        return self._objs[-1]
    
    def remove_object_by_id(self, id: int):
        for obj in self._objs:
            if obj.get_id() == id:
                obj.destroy()
                self._objs.remove(obj)
                return

    def clear_tab(self, tab: int):
        """Apagar todo objeto da tab passada"""
        for obj in self._objs:
            if tab in obj.get_tabs():
                self.remove_object_by_id(obj.get_id())

    def get_objs_with_tags(self, tags: List[str]):
        objs : List[Object] = []
        for obj in self._objs:
            if isinstance(obj, Object):
                is_equal : bool = True
                for tag in obj.tags:
                    if tag not in tags:
                        is_equal = False
                        break
                if is_equal:
                    objs.append(obj)
        return objs

    def fps(self):
        if self.ticks == 0 or self.time_elapsed == 0:
            return 0
        fps_medio = 1 / (self.time_elapsed/self.ticks)
        fps_atual = 1 / self.window.delta_time()
        #if abs(fps_atual - fps_medio) > 10: # se fps atual muito diferente de medio
        return fps_atual
        return fps_medio

    def update(self):
        if self.window.delta_time() > 0:
            self.time_elapsed += self.window.delta_time()
            self.ticks += 1
        
        if self.bg_colors.get(self._tab):
            self.window.set_background_color(self.bg_colors.get(self._tab, 0))
        else:
            self.window.set_background_color("black")
            
        if self.bg_imgs.get(self._tab):
            self.bg.draw()
        
        # aplicar logica
        ids_to_remove : List[int] = []
        for obj in self._objs:
            if not isinstance(obj, Object):
                continue
            if obj.wants_to_die:
                ids_to_remove.append(obj.get_id())
                continue
            # da pra jogar todos os objetos nao usados para o mesmo lugar no limbo, tambem...
            tab_offset : float = 0
            obj.apply_coords(tab_offset, tab_offset)
            if obj.visible and tab_offset == 0 and obj:
                # objeto ativo, atualizar
                obj.delta_time = self.window.delta_time()
                
                h_bounds : Vector2 = Vector2(
                    0 if obj.horizontal_bounds.x == -1 else obj.horizontal_bounds.x,
                    self.window.width if obj.horizontal_bounds.y == -1 else obj.horizontal_bounds.y,
                )

                v_bounds : Vector2 = Vector2(
                    0 if obj.vertical_bounds.x == -1 else obj.vertical_bounds.x,
                    self.window.height if obj.vertical_bounds.y == -1 else obj.vertical_bounds.y,
                )
                
                obj.update()
                
                if obj.keep_in_bounds:
                    obj.pos.x = clamp(obj.pos.x, h_bounds.x, h_bounds.y - obj.get_width())
                    obj.pos.y = clamp(obj.pos.y, v_bounds.x, v_bounds.y - obj.get_height())
                else:
                    obj.out_of_h_bounds = obj.pos.x > h_bounds.y or\
                        obj.pos.x + obj.get_width() < h_bounds.x
                    obj.out_of_v_bounds = obj.pos.y > v_bounds.y or\
                        obj.pos.y + obj.get_height() < v_bounds.x

                obj.out_of_screen = ((obj.pos.x + obj.get_width() < h_bounds.x) or (obj.pos.x > h_bounds.y)) or\
                    ((obj.pos.y + obj.get_height() < v_bounds.x) or (obj.pos.y > v_bounds.y))

                if obj.out_of_h_bounds and obj.destroy_out_of_h_bounds or\
                obj.out_of_v_bounds and obj.destroy_out_of_v_bounds:
                    ids_to_remove.append(obj.get_id())

        for obj_id in ids_to_remove:
            self.remove_object_by_id(obj_id)
        
        # renderizar
        layer : int = 0
        render_buffer = self._objs.copy()
        while len(render_buffer): # enquanto sobrarem elementos
            for obj in render_buffer.copy():
                if not isinstance(obj,Object):
                    render_buffer.remove(obj)
                if obj.z == layer:
                    render_buffer.remove(obj)
                    if self.get_tab() in obj.get_tabs():
                        obj.render() # desenhar elementos dessa camada
            layer += 1
        
        self.window.update()

screen_instance : Screen | None = None

## returns global screen
def get_screen():
    global screen_instance
    if screen_instance is None:
        screen_instance = Screen(TELA_W, TELA_H)
    return screen_instance