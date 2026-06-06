import pygame.transform
from pplay import gameimage as gi
from screen import Object, Vector2, List, EMPTY_PIXEL, res_scale

class TetrisGrid(Object):
    """Grid que serve apenas para mostrar as pecas de tetris.
    A matriz _matrix de inteiros dispoe a informacao de cada
    celula: se for 0 esta vazia, se for 1 esta bloqueada, se
    for 2 esta preenchida e se for 3 esta marcada.
    CHAMAR BUILD GRIDS APOS CRIAR / MEXER NAS PROPRIEDADES"""
    def __init__(self, piece_size : Vector2, linhas : int, colunas : int, tabs: List[int]):
        super().__init__(EMPTY_PIXEL, 1, 1, tabs)
        self._piece_size : Vector2 = Vector2(piece_size.x * res_scale[0], piece_size.y * res_scale[1])
        #self._piece_size : Vector2 = piece_size
        ## quantidade de pecas
        self._lines : int = linhas
        self._columns : int = colunas
        
        # matriz para logica
        self._matrix : List[List[int]] = []
        self.build_matrix()
        
        # matrizes para display
        self._empty_grid   : List[List[gi.GameImage]] = [] # celulas vazias
        self._blocked_grid : List[List[gi.GameImage]] = [] # celulas bloqueadas
        self._filled_grid  : List[List[gi.GameImage]] = [] # celulas preenchidas
        self._marked_grid  : List[List[gi.GameImage]] = [] # celulas preenchidas
        
        # overlay do fundo
        self.overlay_img : str = "assets/images/tech_background_purple_animated.png"
        self.overlay : Object = Object(EMPTY_PIXEL, 0, 0, tabs, add_to_screen=False)
        
        # imagens
        self.EMPTY   : str = "assets/images/tile_empty.png"
        self.BLOCKED : str = "assets/images/tile_blocked.png"
        self.FILLED  : str = "assets/images/tile_filled_purple.png"
        self.MARKED  : str = "assets/images/tile_marked_purple.png"

    def get_width(self):
        if hasattr(self, "_piece_size") and hasattr(self, "_columns"):
            return int(self._piece_size.x * self._columns)
        else:
            return 0
    
    def get_height(self):
        return int(self._piece_size.y * self._lines)
    
    def build_matrix(self):
        self._matrix.clear()
        for i in range(int(self._lines)): # linhas
            self._matrix.append([0] * self._columns)
    
    def build_grid(self, grid : List[List[gi.GameImage]], img : str):
        grid.clear()
        for i in range(self._lines): # linhas
            linha : List[gi.GameImage] = []
            for j in range(self._columns): # colunas
                # adicionar tile
                linha.append(gi.GameImage(img))
                # redimensionar tile
                linha[-1].image = pygame.transform.scale(linha[-1].image, (self._piece_size.x, self._piece_size.y))
            grid.append(linha)
    
    def build_grids(self):
        # criar uma grid de pecas vazia
        self.build_grid(self._empty_grid, self.EMPTY)
        # criar uma grid de pecas bloqueadas
        self.build_grid(self._blocked_grid, self.BLOCKED)
        # criar uma grid de pecas preenchidas
        self.build_grid(self._filled_grid, self.FILLED)
        # criar uma grid de pecas marcadas
        self.build_grid(self._marked_grid, self.MARKED)
        
        self.overlay.wants_to_die = True
        self.overlay = Object(
            self.overlay_img,
            int(self._columns * self._piece_size.x / res_scale[0]),
            int(self._lines * self._piece_size.y / res_scale[1]),
            self.get_tabs(),
            add_to_screen=False)
        self.overlay.set_total_frames(29)
        self.overlay.frame_duration = 0.16
        self.overlay.playing = True
    
    def apply_coords(self, offset_x : float, offset_y : float):
        offset : Vector2 = Vector2(offset_x, offset_y)
        self.update_grid_position(self._empty_grid, offset)
        self.update_grid_position(self._filled_grid, offset)
        self.update_grid_position(self._blocked_grid, offset)
        self.update_grid_position(self._marked_grid, offset)
        self.overlay.apply_coords(offset_x, offset_y)
    
    def update_grid_position(self, grid : List[List[gi.GameImage]], offset : Vector2):
        self.overlay.pos.x = self.pos.x
        self.overlay.pos.y = self.pos.y
        for i in range(int(self._lines)): # linhas
            for j in range(int(self._columns)): # colunas
                grid[i][j].x = self.pos.x + offset.x + self._piece_size.x * j
                grid[i][j].y = self.pos.y + offset.y + self._piece_size.y * i
    
    def animate(self):
        super().animate()
        self.overlay.animate()
    
    def update(self):
        super().update()
        self.overlay.update()
    
    def render(self):
        # desenhar pecas vazias
        for i in range(int(self._lines)): # linhas
            for j in range(int(self._columns)): # colunas    
                    self._empty_grid[i][j].draw()
        # desenhar overlay
        self.overlay.render()
        # desenhar o resto
        for i in range(int(self._lines)): # linhas
            for j in range(int(self._columns)): # colunas
                value = self._matrix[i][j]
                if value == 1:
                    self._blocked_grid[i][j].draw()
                if value == 2:
                    self._filled_grid[i][j].draw()
                if value == 3:
                    self._marked_grid[i][j].draw()