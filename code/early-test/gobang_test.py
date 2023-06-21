# Desc: 智能五子棋
# Auth: ChatGPT
# Requirement: 使用python语言，结合博弈树启发式搜索和alpha-beta剪枝技术，开发一个五子棋博弈游戏。
# Plus:         1. 设计一个15行15列棋盘，要求自行给出估价函数，按极大极小搜索方法，并采用a- β剪枝技术；
#               2. 采用人机对弈方式，对弈双方设置不同颜色的棋子，一方走完一步后，等待对方走步，对弈过程的每个棋局都在屏幕上显示出来。
#               3. 当某一方在横、竖或斜方向上先有5个棋子连成一线时，该方为赢。
# 能力有限，只编写玩家执黑先下的情况:(
# 忽略禁手问题

import numpy as np

# 棋盘大小
BOARD_SIZE = 15

# 定义棋盘状态
EMPTY = 0
BLACK = 1
WHITE = 2

# 定义评估函数中的权重
# 可根据实际情况进行调整
WEIGHTS = {
    "open_two": 10,
    "half_three": 100,
    "open_three": 1000,
    "half_four": 10000,
    "open_four": 100000,
    "five": 1000000
}

# 定义搜索深度
MAX_DEPTH = 2

# 定义搜索方向，包括水平、垂直和对角线
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

# 初始化棋盘
board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

# 人机对弈，根据需要修改
PLAYER_COLOR = BLACK
AI_COLOR = WHITE

# 定义棋局状态
ROUND = 0
PLAYER_ROUND = 1
AI_ROUND = 2


def get_valid_moves(board):
    """
    获取当前棋局的合法移动位置
    """
    moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return moves


def evaluate_position(board):
    """
    评估当前棋局的得分
    """
    score = 0

    def count_stones(line):
        """
        统计一行或一列中连续的棋子个数
        """
        count = 0
        stones = []
        for stone in line:
            if stone == EMPTY:
                if count > 0:
                    stones.append(count)
                    count = 0
            else:
                count += 1
        if count > 0:
            stones.append(count)
        return stones

    # 检查水平方向
    for i in range(BOARD_SIZE):
        line = board[i, :]
        stones = count_stones(line)
        for count in stones:
            if count == 2:
                score += WEIGHTS["open_two"]
            elif count == 3:
                score += WEIGHTS["half_three"]
            elif count == 4:
                score += WEIGHTS["open_four"]
            elif count == 5:
                score += WEIGHTS["five"]

    # 检查垂直方向
    for j in range(BOARD_SIZE):
        line = board[:, j]
        stones = count_stones(line)
        for count in stones:
            if count == 2:
                score += WEIGHTS["open_two"]
            elif count == 3:
                score += WEIGHTS["half_three"]
            elif count == 4:
                score += WEIGHTS["open_four"]
            elif count == 5:
                score += WEIGHTS["five"]

    # 检查对角线方向
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            for direction in DIRECTIONS:
                line = []
                dx, dy = direction
                x, y = i, j
                while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                    line.append(board[x, y])
                    x += dx
                    y += dy
                stones = count_stones(line)
                for count in stones:
                    if count == 2:
                        score += WEIGHTS["open_two"]
                    elif count == 3:
                        score += WEIGHTS["half_three"]
                    elif count == 4:
                        score += WEIGHTS["open_four"]
                    elif count == 5:
                        score += WEIGHTS["five"]

    return score


def is_game_over(board):
    """
    检查游戏是否结束，即是否有一方获胜
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            for direction in DIRECTIONS:
                dx, dy = direction
                x, y = i, j
                count = 0
                while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                    if board[x][y] == board[i][j] & board[i][j] != EMPTY:
                        count += 1
                        if count == 5:
                            return True
                    else:
                        count = 0
                    x += dx
                    y += dy
    return False


def alpha_beta_search(board, depth, alpha, beta, maximizing_player):
    """
    使用Alpha-Beta剪枝进行博弈树搜索
    """
    if depth == 0 or is_game_over(board):
        return evaluate_position(board)

    valid_moves = get_valid_moves(board)
    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            i, j = move
            board[i][j] = AI_COLOR
            eval = alpha_beta_search(board, depth - 1, alpha, beta, False)
            board[i][j] = EMPTY
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            i, j = move
            board[i][j] = PLAYER_COLOR
            eval = alpha_beta_search(board, depth - 1, alpha, beta, True)
            board[i][j] = EMPTY
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def make_ai_move():
    """
    AI进行移动，使用Alpha-Beta剪枝搜索选择最佳位置
    """
    best_score = float('-inf')
    best_move = None
    for move in get_valid_moves(board):
        i, j = move
        board[i][j] = AI_COLOR
        score = alpha_beta_search(board, MAX_DEPTH, float('-inf'), float('inf'), False)
        if score > best_score:
            best_score = score
            best_move = move
        board[i][j] = EMPTY
    if best_move:
        i, j = best_move
        board[i][j] = AI_COLOR


def print_board():
    """
    打印棋盘状态
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == BLACK:
                print("○", end=" ")
            elif board[i][j] == WHITE:
                print("●", end=" ")
            else:
                print("＋", end=" ")
        print()


if __name__ == '__main__':
    # 玩家执黑先行
    ROUND = PLAYER_ROUND
    # 主循环
    while True:
        print_board()
        if ROUND == PLAYER_ROUND:
            x = int(input("请输入行坐标（0-14）："))
            y = int(input("请输入列坐标（0-14）："))
            board[x][y] = PLAYER_COLOR
            ROUND = AI_ROUND
        elif ROUND == AI_ROUND:
            make_ai_move()
            ROUND = PLAYER_ROUND
        else:
            print("回合错误")
            break
        """
        游戏结束，打印最终棋盘状态
        """
        if is_game_over(board):
            print_board()
            print("游戏结束")
            break

