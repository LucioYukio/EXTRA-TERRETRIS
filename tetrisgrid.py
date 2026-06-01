from screen import *

class TetrisGrid(Object):
    """Grid que serve apenas para mostrar as pecas de tetris.
    A matriz _matrix de inteiros dispoe a informacao de cada
    celula: se for 0 esta vazia, se for 1 esta bloqueada e se
    for 2 esta preenchida. CHAMAR BUILD GRIDS APOS CRIAR / MEXER NAS PROPRIEDADES"""
    def __init__(self, piece_size : Vector2, linhas : int, colunas : int, tab: int):
        super().__init__("assets/images/black_pixel.png", 1, 1, tab)
        self._piece_size : Vector2 = piece_size
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
        
        # imagens
        self.EMPTY   : str = "assets/images/tile_empty.png"
        self.BLOCKED : str = "assets/images/tile_blocked.png"
        self.FILLED  : str = "assets/images/tile_filled_green.png"

    
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
    
    def apply_coords(self, offset_x : float, offset_y : float):
        offset : Vector2 = Vector2(offset_x, offset_y)
        self.update_grid_position(self._empty_grid, offset)
        self.update_grid_position(self._filled_grid, offset)
        self.update_grid_position(self._blocked_grid, offset)
    
    def update_grid_position(self, grid : List[List[gi.GameImage]], offset : Vector2):
        for i in range(int(self._lines)): # linhas
            for j in range(int(self._columns)): # colunas
                grid[i][j].x = self.x + offset.x + self._piece_size.x * j
                grid[i][j].y = self.y + offset.y + self._piece_size.y * i
    
    def render(self):
        for i in range(int(self._lines)): # linhas
            for j in range(int(self._columns)): # colunas
                match self._matrix[i][j]:
                    case 1:
                        self._blocked_grid[i][j].draw()
                    case 2:
                        self._filled_grid[i][j].draw()
                    case _:
                        self._empty_grid[i][j].draw()