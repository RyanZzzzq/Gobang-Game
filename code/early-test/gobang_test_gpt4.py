import numpy as np


class Game:
    def __init__(self):
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1
        self.patterns = {
            'five': [100000000, (0, 1, 1, 1, 1, 1, 0)],
            'open_four': [10000000, (0, 1, 1, 1, 1, 0)],
            'half_four': [500000, (-1, 1, 1, 1, 1, 0), (0, 1, 1, 1, 1, -1)],
            'open_three': [50000, (0, 1, 1, 1, 0)],
            'half_three': [5000, (-1, 1, 1, 1, 0), (0, 1, 1, 1, -1)],
            'open_two': [500, (0, 1, 1, 0)]
        }

    def check_patterns(self, row, col):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            line = []
            for i in range(-5, 6):
                x, y = row + i * dx, col + i * dy
                if 0 <= x < 15 and 0 <= y < 15:
                    line.append(self.board[x][y])
                else:
                    line.append(-1)
            for pattern, values in self.patterns.items():
                score, *match = values
                for _ in range(len(line) - len(match) + 1):
                    if line[_:_ + len(match)] == match:
                        return pattern, score
        return None, 0


class AIPlayer:
    def __init__(self, player_id, max_depth=3):
        self.player_id = player_id
        self.max_depth = max_depth
        self.game = Game()

    def select_move(self, board):
        value, move = self.maximize(board, -np.inf, np.inf, 0)
        return move

    def maximize(self, board, alpha, beta, depth):
        if depth == self.max_depth or self.game.check_patterns(board):
            return self.evaluate(board), None

        max_value = -np.inf
        move = None

        for m in self.get_all_moves(board):
            new_board = self.make_move(board, m)
            value, _ = self.minimize(new_board, alpha, beta, depth + 1)

            if value > max_value:
                max_value, move = value, m
                alpha = max(alpha, value)

            if beta <= alpha:
                break

        return max_value, move

    def minimize(self, board, alpha, beta, depth):
        if depth == self.max_depth or self.game.check_patterns(board):
            return self.evaluate(board), None

        min_value = np.inf
        move = None

        for m in self.get_all_moves(board):
            new_board = self.make_move(board, m)
            value, _ = self.maximize(new_board, alpha, beta, depth + 1)

            if value < min_value:
                min_value, move = value, m
                beta = min(beta, value)

            if beta <= alpha:
                break

        return min_value, move

    def evaluate(self, board):
        total_score = 0
        for row in range(15):
            for col in range(15):
                if board[row][col] == self.player_id:
                    _, score = self.game.check_patterns(row, col)
                    total_score += score
        return total_score

    def get_all_moves(self, board):
        return [(i, j) for i in range(15) for j in range(15) if board[i][j] == 0]

    def make_move(self, board, move):
        new_board = [row.copy() for row in board]
        new_board[move[0]][move[1]] = self.player_id
        return new_board


def print_board(board):
    print('  ', end='')
    for i in range(15):
        print(f'{i:2d}', end=' ')
    print()
    for i in range(15):
        print(f'{i:2d}', end=' ')
        for j in range(15):
            if board[i][j] == 0:
                print(' .', end=' ')
            elif board[i][j] == 1:
                print(' X', end=' ')
            else:
                print(' O', end=' ')
        print()


def main():
    player1 = AIPlayer(1)
    player2 = AIPlayer(2)

    board = [[0 for _ in range(15)] for _ in range(15)]
    current_player = player1
    while True:
        print_board(board)
        if isinstance(current_player, AIPlayer):
            row, col = current_player.select_move(board)
        else:
            row, col = map(int, input("Enter your move: ").split())
        board[row][col] = current_player.player_id
        if current_player == player1:
            current_player = player2
        else:
            current_player = player1
        if player1.game.check_patterns(board)[0] == 'five' or player2.game.check_patterns(board)[0] == 'five':
            print('Game Over.')
            break


if __name__ == "__main__":
    main()
