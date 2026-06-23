from copy import copy
import random

from screen import Object, Vector2, List, EMPTY_PIXEL, get_screen
from typing import Tuple
import sounds
from tetrisgrid import TetrisGrid

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
        
        sounds.TETRIS_RODAR.stop()
        sounds.TETRIS_RODAR.play()
    
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

## peca em formato de L
PECA_L1 : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [1, 1, 1], # escrever matrix da forma aqui, desse jeito
        [0, 0, 1],
    ], center=(0, 1)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [0, 1],
        [0, 1],
        [1, 1],
    ], center=(1, 1)),
    # terceira forma
    Form(matrix=[
        [1, 0, 0],
        [1, 1, 1],
    ], center=(1, 1)),
    # quarta forma
    Form(matrix=[
        [1, 1],
        [1, 0],
        [1, 0],
    ], center=(1, 0)),
])

## peca em formato de L'
PECA_L2 : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [0, 0, 1], # escrever matrix da forma aqui, desse jeito
        [1, 1, 1],
    ], center=(1, 1)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [1, 0],
        [1, 0],
        [1, 1],
    ], center=(1, 0)),
    # terceira forma
    Form(matrix=[
        [1, 1, 1],
        [1, 0, 0],
    ], center=(0, 1)),
    # quarta forma
    Form(matrix=[
        [1, 1],
        [0, 1],
        [0, 1],
    ], center=(1, 1)),
])

## peca em formato de S
PECA_S1 : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [0, 1, 1], # escrever matrix da forma aqui, desse jeito
        [1, 1, 0],
    ], center=(0, 1)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [1, 0],
        [1, 1],
        [0, 1],
    ], center=(1, 1)),
])

## peca em formato de S'
PECA_S2 : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [1, 1, 0], # escrever matrix da forma aqui, desse jeito
        [0, 1, 1],
    ], center=(0, 1)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [0, 1],
        [1, 1],
        [1, 0],
    ], center=(1, 1)),
])

## peca em formato de quadrado
PECA_Q : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [1, 1], # escrever matrix da forma aqui, desse jeito
        [1, 1],
    ], center=(0, 0))
])

## peca em formato de I
PECA_I : Piece = Piece([
    # primeira forma
    Form(matrix=[
        [1], # escrever matrix da forma aqui, desse jeito
        [1],
        [1],
        [1],
    ], center=(1, 0)), # centro dessa forma
    # segunda forma
    Form(matrix=[
        [1, 1, 1, 1],
    ], center=(0, 1))
])


## peca vazia; NULL
PECA_NULL : Piece = Piece([FORM_NULL])
    
class Tetris(Object):
    """Esse objeto possui uma matriz propria para logica,
    nao eh a mesma que a grid. Quano o render() desse objeto
    eh chamado, ele envia para a matrix da grid a matrix
    desse objeto + a peca atual."""
    def __init__(self, piece_size: Vector2, linhas: int, colunas: int, tabs: List[int], h_parts: int = 1):
        super().__init__(EMPTY_PIXEL, 0, 0, tabs, h_parts)
        self.keyboard = get_screen().keyboard
        self.grid : TetrisGrid = TetrisGrid(piece_size, linhas, colunas, tabs)
        
        self.lines : int = linhas
        self.columns : int = colunas
        self.points : int = 0 # accumulated points. Flush this to the aura counter in the game loop!
        
        self.matrix : List[List[int]] = []
        self.build_matrix()
        
        # copiar tudo para ter uma instancia propria de cada peca
        self.piece_pool : List[Piece] = [copy(PECA_T), copy(PECA_L1), copy(PECA_L2), copy(PECA_Q), copy(PECA_I), copy(PECA_S1), copy(PECA_S2)] # pecas que serao possiveis serem escolhidas
        # ATENCAO: reiniciar posicao da peca sempre que terminar/comecar a usa-la (fica a seu criterio)
        self.curr_piece : Piece = PECA_NULL # peca escolhida no momento;
        
        self.gravity_speed: float = 1 # velocidade da gravidade; passiva
        self.gravity_increment_interval: float = 10 # intervalo entre aumentos de gravidade
        self.gravity_increment_cooldown: float = self.gravity_increment_interval
        self.gravity_increment_value: float = 0.1 # valor adicionado a gravidade periodicamente
        
        self.piece_fall_speed: float = 10 # velocidade da caida acelerada da peca; ativa
        
        # intervalos
        self.rotation_interval: float = 0.2 # intervalo entre rotacoes
        self.rotation_cooldown: float = 0
        self.side_step_interval: float = 0.2 # intervalo entre andadas para o lado
        self.side_step_cooldown: float = 0
        
        # teclas
        self.UP    : str = "w"
        self.DOWN  : str = "s"
        self.LEFT  : str = "a"
        self.RIGHT : str = "d"
        self.SPIN  : str = "space"
        self.POWER : str = "alt"
        
        self.lost : bool = False

        self.choice_piece()

    def build_matrix(self):
        self.matrix = [[0] * self.columns for _ in range(self.lines)]
        self.grid.build_grids()

    def check_loss(self):
        for tile in self.matrix[0]:
            if tile != 0:
                self.lost = True
                return True
        return False

    def reset(self):
        self.lost = False
        self.points = 0
        self.gravity_speed = 1
        self.gravity_increment_cooldown = self.gravity_increment_interval
        self.build_matrix()
        self.choice_piece()

    def handle_filled_lines(self):
        # checa se alguma linha esta cheia.
        # se sim, apaga a linha e incrementa um ponto
        sequencia = 0
        for linha in self.matrix:
            cheia = True
            for tile in linha:
                if tile != 2:
                    cheia = False
            if cheia:
                self.matrix.remove(linha)
                self.matrix.insert(0, [0] * self.columns)
                self.points += 1 + sequencia
                sequencia += 1
                
                sounds.TETRIS_LIMPA_LINHA.stop()
                sounds.TETRIS_LIMPA_LINHA.play()


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
        self.grid.pos.x = self.pos.x
        self.grid.pos.y = self.pos.y

        old_line = self.curr_piece.line
        old_column = self.curr_piece.column
        old_rotation = self.curr_piece.rotation

        self.curr_piece.line += self.gravity_speed * self.delta_time # gravidade

        if self.keyboard.key_pressed(self.DOWN):
            self.curr_piece.line += self.piece_fall_speed * self.delta_time

        if self.side_step_cooldown <= 0:
            if self.keyboard.key_pressed(self.LEFT) and self.curr_piece.column > 0:
                # joga pra coluna esquerda
                self.curr_piece.column -= 1
                self.side_step_cooldown = self.side_step_interval
                if self.check_collision_wall(self.curr_piece) or self.check_collision_tiles(self.curr_piece):
                    self.curr_piece.column = old_column # undo movement
            if self.keyboard.key_pressed(self.RIGHT) and self.curr_piece.column < (self.columns) - self.curr_piece.get_columns():
                # joga pra coluna direita
                self.curr_piece.column += 1
                self.side_step_cooldown = self.side_step_interval
                if self.check_collision_wall(self.curr_piece) or self.check_collision_tiles(self.curr_piece):
                    self.curr_piece.column = old_column # undo movement
        else:
            self.side_step_cooldown -= self.delta_time

        if self.rotation_cooldown <= 0 and (self.keyboard.key_pressed(self.SPIN) or self.keyboard.key_pressed(self.UP)):
            self.curr_piece.rotate()
            if self.check_collision_wall(self.curr_piece) or self.check_collision_tiles(self.curr_piece):
                self.curr_piece.rotate(-1)
            self.rotation_cooldown = self.rotation_interval
        else:
            self.rotation_cooldown -= self.delta_time

        if self.check_collision(self.curr_piece): # se bateu
            # volta a ser como era antes dos movimentos
            self.curr_piece.rotation = old_rotation
            self.curr_piece.line = old_line
            self.curr_piece.column = old_column

            self.lock_piece()
            self.choice_piece()

        if self.gravity_increment_cooldown <= 0:
            self.gravity_speed += self.gravity_increment_value
            self.gravity_increment_cooldown = self.gravity_increment_interval
        else:
            self.gravity_increment_cooldown -= self.delta_time

        self.grid.update()
        self.handle_filled_lines()
    
    def apply_coords(self):
        super().apply_coords()
        self.grid.apply_coords()

    def check_collision_tiles(self, piece: Piece):
        """retorna se colidiu ou nao com algum tile"""
        if self.check_collision_floor(piece):
            return True
        forma = piece.get_form()
        for i in range(forma.get_lines()):
            for j in range(forma.get_columns()):
                if forma.matrix[i][j] == 0:
                    continue
                linha = int(piece.line) + i
                coluna = int(piece.column) + j
                # bateu em bloco já existente
                if linha >= 0 and self.matrix[linha][coluna] != 0:
                    return True
        return False

    def check_collision_wall(self, piece: Piece):
        """retorna se saiu ou nao da grid"""
        forma = piece.get_form()
        for i in range(forma.get_lines()):
            for j in range(forma.get_columns()):
                if forma.matrix[i][j] == 0:
                    continue
                coluna = int(piece.column) + j
                if coluna < 0 or coluna >= self.columns:
                    return True
        return False

    def check_collision_floor(self, piece: Piece):
        """retorna se bateu no chao"""
        forma = piece.get_form()
        for i in range(forma.get_lines()):
            for j in range(forma.get_columns()):
                if forma.matrix[i][j] == 0:
                    continue
                linha = int(piece.line) + i
                # fora da tela
                if linha >= self.lines:
                    return True
        return False
    
    def check_collision(self, piece: Piece):
        """retorna se colidiu ou nao com o chao ou com um tile"""
        return self.check_collision_floor(piece) or self.check_collision_tiles(piece)
    
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

    def lock_piece(self):
        forma = self.curr_piece.get_form()

        for i in range(forma.get_lines()):
            for j in range(forma.get_columns()):

                if forma.matrix[i][j] == 0:
                    continue

                linha = int(self.curr_piece.line) + i
                coluna = int(self.curr_piece.column) + j

                self.matrix[linha][coluna] = 2
            
        sounds.TETRIS_COLAR.stop()
        sounds.TETRIS_COLAR.play()

    def choice_piece(self):
        old_piece = self.curr_piece
        while old_piece == self.curr_piece:
            self.curr_piece = random.choice(self.piece_pool)
        self.curr_piece.line = 0
        self.curr_piece.column = self.columns // 2 - self.curr_piece.get_columns()//2
    
    def render(self):
        # transferir peca
        forma : Form = self.curr_piece.get_form()
        for i in range(self.lines):
            for j in range(self.columns):
                value : int = 0
                if i >= int(self.curr_piece.line) and i < int(self.curr_piece.line) + self.curr_piece.get_lines() and\
                    j >= int(self.curr_piece.column) and j < int(self.curr_piece.column) + self.curr_piece.get_columns():
                        value = forma.matrix[i - int(self.curr_piece.line)][j - int(self.curr_piece.column)] * 3
                if value != 3:
                    value = self.matrix[i][j]
                self.grid._matrix[i][j] = value
        
        self.grid.render()
        
    