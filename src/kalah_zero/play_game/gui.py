from logging import getLogger


from kalah_zero.config import Config, PlayWithHumanConfig
from kalah_zero.play_game.game_model import PlayWithHuman
from kalah_zero.env.kalah_env import KalahEnv, Player, Winner
from random import random

logger = getLogger(__name__)


def start(config: Config):
    PlayWithHumanConfig().update_play_config(config.play)
    kalah_model = PlayWithHuman(config)


    env = KalahEnv().reset()
    human_is_black = random() < 0.5
    kalah_model.start_game(human_is_black)

    while not env.done:
        if env.player_turn == Player.black:
            if not human_is_black:
                action = kalah_model.move_by_ai(env)
                print("IA moves to: " + str(action + 1))
            else:
                action = kalah_model.move_by_human(env)
                print("You move to: " + str(action + 1))
        else:
            if human_is_black:
                action = kalah_model.move_by_ai(env)
                print("IA moves to: " + str(action + 1))
            else:
                action = kalah_model.move_by_human(env)
                print("You move to: " + str(action + 1))
        env.step(action)
        env.render()

    print("\nEnd of the game.")
    print("Game result:")
    if env.winner == Winner.white:
        print("X wins")
    elif env.winner == Winner.black:
        print("O wins")
    else:
        print("Game was a draw")
