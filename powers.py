
"""
Poderes sao mudancas instantaneas ou efeitos temporarios que sao ativados pelo player.
Se o player ativar um poder e ele ja estiver com um poder do tipo ativado,
ele reinicia a duracao do poder (quando eh do tipo efeito temporario).

"""

NAVE_TEMPO = 0 # deixa tudo do lado da nave mais devagar por um tempo # idealmente, o que esta mais perto fica mais lento, mas nao eh necessario
NAVE_VIDA = 1 # restaura 1 de vida da nave
NAVE_DANO = 2 # aumenta o dano da nave por um tempo