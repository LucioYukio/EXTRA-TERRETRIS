from pplay.window import Window
from screen import *
from tetrisgrid import *

# Dica(?): recomendo evitar usar vector2 aqui pois
# linha = y e coluna = x, o que pode confundir.
# Use Listas de dois valores, por exemplo. 

class Form:
    """Uma forma de uma peca de tetris, contendo
    os blocos que formam a forma e onde eh o centro dela.
    Manter self.form em forma de matrix! Ou seja, todas as colunas
    tem o mesmo tamanho e todas as linhas tambem!!!!"""
    def __init__(self, matrix : List[List[int]], center: Tuple[int, int]) -> None:
        self.matrix : List[List[int]] = matrix
        self.center : Tuple[int, int] = center # centro da forma (linha, coluna)
    
    def get_lines(self):  # retorna quantas linhas a forma tem
        if self.matrix: # se nao esta vazia
            return len(self.matrix)
        else:
            return 0
    
    def get_columns(self):  # retorna quantas colunas a forma tem
        if self.matrix: # se nao esta vazia
            return len(self.matrix[0])
        else:
            return 0

## forma vazia; NULL
FORM_NULL : Form = Form([], (0,0))

class Piece:
    """Peca de Tetris, contendo posicao, 
    rotacao atual e forma pra cada rotacao"""
    def __init__(self, formas: List[Form]) -> None:
        self.line  : float = 0 # linha em que o canto superior esquerdo da peca esta
        self.column : float = 0 # coluna em que o canto superior esquerdo da peca esta
        self.rotation : int = 0 # qual a forma escolida em relacao a lista de formas dessa peca
        self.forms : List[Form] = formas # formas possiveis, em ordem
    
    def rotate(self, amount: int = 1): # vai para proximo formato; loopar se no final
        center = self.get_form().center
        self.line += center[0]
        self.column += center[1]
        self.rotation = (self.rotation + amount) % len(self.forms)
        center = self.get_form().center
        self.line -= center[0]
        self.column -= center[1]
    
    def get_form(self):
        if self.forms:
            return self.forms[self.rotation]
        return FORM_NULL
        
    def get_lines(self):
        if self.forms:
            return self.get_form().get_lines()
        else:
            return 0
    
    def get_columns(self):
        if self.forms:
            return self.get_form().get_columns()
        else:
            return 0

# PECAS:

## peca em formato de T
PECA_T : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [1, 1, 1], # escrever matrix da forma aqui, desse jeito
        [0, 1, 0],
    ], center=(0, 1)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [0, 1],
        [1, 1],
        [0, 1],
    ], center=(1, 1)),
    # terceira forma
    Form(matrix=[
        [0, 1, 0],
        [1, 1, 1],
    ], center=(1, 1)),
    # quarta forma
    Form(matrix=[
        [1, 0],
        [1, 1],
        [1, 0],
    ], center=(1, 0)),
])

## peca vazia; NULL
PECA_NULL : Piece = Piece([FORM_NULL])
    
class Tetris(Object):
    """Esse objeto possui uma matriz propria para logica,
    nao eh a mesma que a grid. Quano o render() desse objeto
    eh chamado, ele envia para a matrix da grid a matrix
    desse objeto + a peca atual."""
    def __init__(self, piece_size: Vector2, linhas: int, colunas: int, tab: int, h_parts: int = 1):
        super().__init__(EMPTY_PIXEL, 0, 0, tab, h_parts)
        self.keyboard = get_screen().keyboard
        self.grid : TetrisGrid = TetrisGrid(piece_size, linhas, colunas, tab)
        
        self.lines : int = linhas
        self.columns : int = colunas
        
        self.matrix : List[List[int]] = []
        self.build_matrix()
        
        self.piece_pool : List[Piece] = [PECA_T, ] # pecas que serao possiveis serem escolhidas
        # ATENCAO: reiniciar posicao da peca sempre que terminar/comecar a usa-la (fica a seu criterio)
        self.curr_piece : Piece = PECA_T # peca escolhida no momento;
        
        # velocidades; em quadradinhos por segundo; tiles/second
        self.gravity_speed: float = 1 # velocidade da gravidade; passiva
        self.piece_fall_speed: float = 10 # velocidade da caida acelerada da peca; ativa
        
        # intervalos
        self.rotation_interval: float = 0.2 # intervalo entre rotacoes
        self.rotation_cooldown: float = 0
        self.side_step_interval: float = 0.2 # intervalo entre andadas para o lado
        self.side_step_cooldown: float = 0
        
        # teclas
        self.DOWN  : str = "s"
        self.LEFT  : str = "a"
        self.RIGHT : str = "d"
        self.SPIN  : str = "space"
        self.POWER : str = "alt"
        
        
    def build_matrix(self):
        self.matrix = [[0] * self.columns for _ in range(self.lines)]
        self.grid.build_grids()
    
    ## preenche a ultima posicao livre
    def add_filled_at_end(self):
        # get last empty pos
        last_empty_pos = [0,0]
        for i in range(self.lines):
            for j in range(self.columns):
                if self.matrix[i][j] == 0:
                    last_empty_pos = [i, j]
        # fill
        self.matrix[last_empty_pos[0]][last_empty_pos[1]] = 2
    
    def add_blocked_line_bellow(self):
        self.matrix.pop(0)
        self.matrix.append([1] * self.columns)
    
    def update(self):
        super().update()
        self.grid.x = self.x
        self.grid.y = self.y
        
        self.curr_piece.line += self.gravity_speed * self.delta_time
        
        if self.keyboard.key_pressed(self.DOWN):
            self.curr_piece.line += self.piece_fall_speed * self.delta_time
        
        if self.side_step_cooldown <= 0:
            if self.keyboard.key_pressed(self.LEFT) and self.curr_piece.column > 0:
                self.curr_piece.column -= 1
                self.side_step_cooldown = self.side_step_interval    
            if self.keyboard.key_pressed(self.RIGHT) and self.curr_piece.column < (self.columns) - self.curr_piece.get_columns():
                self.curr_piece.column += 1
                self.side_step_cooldown = self.side_step_interval
        else:
            self.side_step_cooldown -= self.delta_time
        
        if self.rotation_cooldown <= 0 and self.keyboard.key_pressed(self.SPIN):
            self.curr_piece.rotate()
            self.rotation_cooldown = self.rotation_interval
        else:
            self.rotation_cooldown -= self.delta_time
            
        self.grid.update()
    
    def apply_coords(self, offset_x: float, offset_y: float):
        super().apply_coords(offset_x, offset_y)
        self.grid.apply_coords(offset_x, offset_y)
    
    def get_height(self):
        if hasattr(self, "grid"):
            return self.grid.get_height()
        else:
            return 0
    
    def get_width(self):
        if hasattr(self, "grid"):
            return self.grid.get_width()
        else:
            return 0
    
    def render(self):
        # transferir peca
        forma : Form = self.curr_piece.get_form()
        for i in range(self.lines):
            for j in range(self.columns):
                value : int = 0
                
                if i >= int(self.curr_piece.line) and i < int(self.curr_piece.line) + self.curr_piece.get_lines() and\
                    j >= int(self.curr_piece.column) and j < int(self.curr_piece.column) + self.curr_piece.get_columns():
                        value = forma.matrix[i - int(self.curr_piece.line)][j - int(self.curr_piece.column)] * 2
                if value != 2:
                    value = self.matrix[i][j]
                self.grid._matrix[i][j] = value
        
        self.grid.render()
        
    