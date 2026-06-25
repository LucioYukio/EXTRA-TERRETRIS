from pplay.sound import Sound

# nave
MUSICA             = Sound("assets/sounds/musica.ogg"   )
TIRO               = Sound("assets/sounds/tiro.ogg"     )
ACERTO             = Sound("assets/sounds/acerto.ogg"   )
DANO               = Sound("assets/sounds/dano.ogg"     )
EXPLOSAO           = Sound("assets/sounds/explosion.ogg")
ASTEROIDE          = Sound("assets/sounds/asteroid.ogg" )

# tetris
TETRIS_LIMPA_LINHA = Sound("assets/sounds/tetris_line_clear.ogg")
TETRIS_RODAR       = Sound("assets/sounds/tetris_spin.ogg"      )
TETRIS_COLAR       = Sound("assets/sounds/tetris_glue.ogg"      )

# poderes - nave
HEAL_NAVE          = Sound("assets/sounds/heal.ogg")
KILL_ALL           = Sound("assets/sounds/kill_all.ogg")
SLOW_DOWN          = Sound("assets/sounds/slow_down.ogg")
SHIELD_NAVE        = Sound("assets/sounds/shield.ogg")
SIDE_SHOT          = Sound("assets/sounds/tiro_alt.ogg")

# poderes - tetris
BLOCKED_BAR        = Sound("assets/sounds/blocked_bar.ogg")
ERASE_BOTTOM       = Sound("assets/sounds/erase_bottom.ogg")
NEW_PIECE          = Sound("assets/sounds/new_piece.ogg")

# geral
ROUND_END          = Sound("assets/sounds/next_confront.ogg")
ROUND_END.set_volume(100)
BUTTON             = Sound("assets/sounds/button.ogg"       )
SABOTAGE_INCOMING  = Sound("assets/sounds/sabotage_incoming.ogg")
BOUGHT             = Sound("assets/sounds/bought.ogg"       )
