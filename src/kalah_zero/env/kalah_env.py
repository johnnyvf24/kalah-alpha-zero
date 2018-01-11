import enum
import numpy as np

from logging import getLogger

logger = getLogger(__name__)

# noinspection PyArgumentList
Winner = enum.Enum("Winner", "black white draw")

# noinspection PyArgumentList
Player = enum.Enum("Player", "black white")


class KalahEnv:
    def __init__(self):
        self.board = None
        self.turn = 0
        self.done = False
        self.winner = None  # type: Winner
        self.resigned = False

    def reset(self):
        self.board = [None] * 14
        self.num_stones = 4
        for i in range(len(self.board)):
            if i < 6:
                self.board[i] = self.num_stones
            elif i > 6 and i < 13:
                self.board[i] = self.num_stones
            else:
                self.board[i] = 0
        self.player_turn = Player.white
        self.done = False
        self.winner = None
        self.moves_made = 0
        self.resigned = False
        return self

    def update(self, board, player_turn, moves_made):
        self.board = np.copy(board)
        self.moves_made = moves_made
        self.player_turn = player_turn
        self.done = False
        self.winner = None
        self.resigned = False
        return self

    def step(self, action, verbose=False):
        """
        :return:
        """
        assert action is None or 0 <= action <= 13, f"Illegal action={action}"

        if action is None:
            self._resigned()
            return self.board, {}

        if verbose == True:
            print (self.player_turn)
            self.render()

        if self.player_turn == Player.white:
            enemy_kalah = 13
            own_kalah = 6
        else:
            enemy_kalah = 6
            own_kalah = 13
            action = 12 - action # Necessary to account for other player's kalah

        # Pick up stones
        stones = self.board[action]
        self.board[action] = 0

        # Start going around the board
        index = action + 1
        while stones > 0:
            # Don't place stones in enemy kalah
            if index != enemy_kalah:
                self.board[index] += 1
                stones -= 1
            index = (index + 1) % 14
        if index == 0:
            index = 14
        lastIndex = index - 1

        # Special condition 1
        if self.board[lastIndex] == 1 and lastIndex != own_kalah:
            if self.player_turn == Player.white and lastIndex < 6:
                self.last_stone_into_empty_bowl(lastIndex)
            elif self.player_turn == Player.black and lastIndex > 6:
                self.last_stone_into_empty_bowl(lastIndex)

        # Special condition 2
        go_again = False
        if lastIndex == own_kalah:
            if verbose == True:
                print('go again')
            go_again = True

        if go_again == False:
            self.set_next_turn()

        self.moves_made += 1
        has_move = self.has_move()
        opponent_has_move = self.opponent_has_move()

        if self.moves_made > 65:
            self.done = True
            if self.winner is None:
                self.winner = Winner.draw

        if has_move == False or opponent_has_move == False:
            self.distribute_final_stones()

        return self.board, {}

    def has_move(self):
        has_move = False
        legal_moves = self.legal_moves()
        for i in range(len(legal_moves)):
            if legal_moves[i] == 1:
                has_move = True
        return has_move

    def opponent_has_move(self):
        self.set_next_turn()
        has_move = self.has_move()
        self.set_next_turn()
        return has_move

    def distribute_final_stones(self):
        for i in range(6):
            self.board[6] += self.board[i]
            self.board[i] = 0;
        for i in range (7, 13):
            self.board[13] += self.board[i]
            self.board[i] = 0;
        self.done = True
        if self.board[6] == self.board[13]:
            self.winner = Winner.draw
        elif self.board[6] > self.board[13]:
            self.winner = Winner.white
        else:
            self.winner = Winner.black

    def set_next_turn(self):
        if self.player_turn == Player.white:
            self.player_turn = Player.black
        elif self.player_turn == Player.black:
            self.player_turn = Player.white

    def last_stone_into_empty_bowl(self, lastIndex):
        if lastIndex < 6:
            oppositeBowl = (12 - 2 * lastIndex) + lastIndex
            if self.board[oppositeBowl] != 0:
                totStones = self.board[oppositeBowl] + 1
                self.board[6] += totStones
                self.board[oppositeBowl] = 0
                self.board[lastIndex] = 0
        elif lastIndex > 6:
            oppositeBowl = 12 - lastIndex
            if self.board[oppositeBowl] != 0:
                totStones = self.board[oppositeBowl] + 1
                self.board[13] += totStones
                self.board[oppositeBowl] = 0
                self.board[lastIndex] = 0

    def legal_moves(self):
        legal = [0, 0, 0, 0, 0, 0]
        if self.player_turn == Player.white:
            for i in range(6):
                if self.board[i] != 0:
                    legal[i] = 1
        elif self.player_turn == Player.black:
            for i in range(7, 13):
                if self.board[i] != 0:
                    legal[12-i] = 1

        return legal

    def get_player_turn(self):
        if self.player_turn == Player.white:
            return 0
        else:
            return 1

    def _resigned(self):
        if self.player_turn == Player.white:
            self.winner = Winner.white
        else:
            self.winner = Winner.black
        self.done = True
        self.resigned = True

    def black_and_white_plane(self):
        board_white = np.copy(self.board)
        board_black = np.copy(self.board)
        for i in range(len(self.board)):
            if i < 7: # includes white kalah
                board_black[i] = 0
                board_white[i] = self.board[i]
            elif i > 6: # includes black kalah
                board_black[i] = self.board[i]
                board_white[i] = 0

        return np.array(board_white), np.array(board_black)

    def render(self):
        print(f"\t{self.board[12]}\t{self.board[11]}\t{self.board[10]}\t{self.board[9]}\t{self.board[8]}\t{self.board[7]}")
        print(f"{self.board[13]}\t\t\t\t\t\t\t{self.board[6]}")
        print(f"\t{self.board[0]}\t{self.board[1]}\t{self.board[2]}\t{self.board[3]}\t{self.board[4]}\t{self.board[5]}")

    @property
    def observation(self):
        """
        :rtype: Board
        """
        return '-'.join(str(x) for x in self.board)
