from .game import Game


def play_game(dificuldade: str = "normal", win_points: int = 3):
    Game(dificuldade, win_points).run()
