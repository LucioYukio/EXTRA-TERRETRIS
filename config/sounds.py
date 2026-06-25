import os
import sys

from pplay.sound import Sound


def _resolve(path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, path)
    return path


def _sound(path: str) -> Sound:
    return Sound(_resolve(path))


# nave
MUSICA             = _sound("assets/sounds/musica.ogg"   )
TIRO               = _sound("assets/sounds/tiro.ogg"     )
ACERTO             = _sound("assets/sounds/acerto.ogg"   )
DANO               = _sound("assets/sounds/dano.ogg"     )
EXPLOSAO           = _sound("assets/sounds/explosion.ogg")
ASTEROIDE          = _sound("assets/sounds/asteroid.ogg" )

# tetris
TETRIS_LIMPA_LINHA = _sound("assets/sounds/tetris_line_clear.ogg")
TETRIS_RODAR       = _sound("assets/sounds/tetris_spin.ogg"      )
TETRIS_COLAR       = _sound("assets/sounds/tetris_glue.ogg"      )

# poderes - nave
HEAL_NAVE          = _sound("assets/sounds/heal.ogg")
KILL_ALL           = _sound("assets/sounds/kill_all.ogg")
SLOW_DOWN          = _sound("assets/sounds/slow_down.ogg")
SHIELD_NAVE        = _sound("assets/sounds/shield.ogg")
SIDE_SHOT          = _sound("assets/sounds/tiro_alt.ogg")

# poderes - tetris
BLOCKED_BAR        = _sound("assets/sounds/blocked_bar.ogg")
ERASE_BOTTOM       = _sound("assets/sounds/erase_bottom.ogg")
NEW_PIECE          = _sound("assets/sounds/new_piece.ogg")

# geral
ROUND_END          = _sound("assets/sounds/next_confront.ogg")
ROUND_END.set_volume(100)
BUTTON             = _sound("assets/sounds/button.ogg"       )
SABOTAGE_INCOMING  = _sound("assets/sounds/sabotage_incoming.ogg")
BOUGHT             = _sound("assets/sounds/bought.ogg"       )
