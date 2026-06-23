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

# geral
ROUND_END          = Sound("assets/sounds/next_confront.ogg")
ROUND_END.set_volume(100)
BUTTON             = Sound("assets/sounds/button.ogg"       )
SABOTAGE_INCOMING  = Sound("assets/sounds/sabotage_incoming.ogg")
BOUGHT             = Sound("assets/sounds/bought.ogg"       )
