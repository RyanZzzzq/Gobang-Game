import numpy as np


class Game:
    def __init__(self):
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1
        self.patterns = {
            'five': [100000000, [(1, 1, 1, 1, 1)]],
            'open_four': [10000000, [(-1, 1, 1, 1, 1, -1)]],
            'half_four': [500000, [(0, 1, 1, 1, 1, -1), (-1, 1, 1, 1, 1, 0)]],
            'open_three': [50000, [(-1, 1, 1, 1, -1)]],
            'half_three': [5000, [(0, 1, 1, 1, -1), (-1, 1, 1, 1, 0)]],
            'open_two': [500, [(-1, 1, 1, -1)]]
        }

    def check_patterns(self, board):
        max_pattern = None
        max_score = 0
        for row in range(15):
            for col in range(15):
                for pattern, values in self.patterns.items():
                    score = values[0]
                    for sub_pattern in values[1]:
                        if self.match_pattern(board, row, col, sub_pattern):
                            if score > max_score:
                                max_pattern = pattern
                                max_score = score
                            break
        return max_pattern, max_score

    def match_pattern(self, board, row, col, sub_pattern):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            for i in range(len(sub_pattern)):
                x, y = row + dx * i, col + dy * i
                if x < 0 or x >= 15 or y < 0 or y >= 15 or (sub_pattern[i] != -1 and board[x][y] != sub_pattern[i]):
                    break
            else:
                return True
        return False


class AIPlayer:
    def __init__(self, player_id):
        self.player_id = player_id
        self.game = Game()

    def select_move(self, board):
        _, move = self.maximize(board, -np.inf, np.inf, 0)
        if move is None:  # if all moves are pruned, select the first available move
            move = next((i, j) for i in range(15) for j in range(15) if board[i][j] == 0)
        return move

    def maximize(self, board, alpha, beta, depth):
        if depth == 0 or self.game.check_patterns(board)[0] == "five":
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

        return max_value, move or (0, 0)

    def minimize(self, board, alpha, beta, depth):
        if depth == 0 or self.game.check_patterns(board)[0] == "five":
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

        return min_value, move or (0, 0)

        # Evaluate the board situation from the perspective of the AI player.

    def evaluate(self, board):
        pattern, score = self.game.check_patterns(board)
        if pattern is None:
            return 0
        else:
            return score if any(
                board[i][j] == self.player_id for i in range(15) for j in range(15) if board[i][j] != 0) else -score

        # Get all possible moves in the current board situation.

    def get_all_moves(self, board):
        return [(i, j) for i in range(15) for j in range(15) if board[i][j] == 0]

        # Simulate a move on the board and return the new board situation.

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
    current_player = player1

    board = [[0 for _ in range(15)] for _ in range(15)]
    while True:
        print_board(board)
        if current_player == player1:
            row, col = player1.select_move(board)
            board[row][col] = player1.player_id
            current_player = 'player2'
        else:
            row, col = map(int, input("Enter your move (row col): ").split())
            while board[row][col] != 0:
                print("Invalid move. Please try again.")
                row, col = map(int, input("Enter your move (row col): ").split())
            board[row][col] = 2
            current_player = player1

        if player1.game.check_patterns(board)[0] == 'five':
            print('AI won the game!')
            break
        elif any(player1.game.check_patterns((i, j))[0] == 'five' for i in range(15) for j in range(15) if board[i][j] == 2):
            print('Human player won the game!')
            break


if __name__ == "__main__":
    main()
