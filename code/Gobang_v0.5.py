"""
-*- coding: utf-8 -*-
Desc: 智能五子棋
Auth: Zhou Ziqi
GitHub：RyanZzzzq
Requirement: 使用python语言，结合博弈树启发式搜索和alpha-beta剪枝技术，开发一个五子棋博弈游戏。
Plus:   1. 设计一个15行15列棋盘，要求自行给出估价函数，按极大极小搜索方法，并采用α-β剪枝技术；
        2. 采用人机对弈方式，对弈双方设置不同颜色的棋子，一方走完一步后，等待对方走步，对弈过程的每个棋局都在屏幕上显示出来；
        3. 当某一方在横、竖或斜方向上先有5个棋子连成一线时，该方为赢。
PS:能力有限:( ，只编写玩家执黑先下情况，且忽略禁手问题
Version: v0.5
"""

import numpy as np
import time

# 棋盘大小
BOARD_SIZE = 15

# 定义棋盘状态
EMPTY = 0
BLACK = 1
WHITE = 2

# 定义评估函数中的权重
# 可根据实际情况进行调整
WEIGHTS = {
    "open_two": 10,       # 活二
    "half_three": 100,    # 死三
    "open_three": 1000,   # 活三
    "half_four": 10000,   # 死四
    "open_four": 100000,  # 活四
    "five": 1000000       # 五连
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


def evaluate_position(board, color):
    """
    评估当前棋局的得分
    """
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == color:
                for dx, dy in DIRECTIONS:
                    if 0 <= i + 4 * dx < BOARD_SIZE and 0 <= j + 4 * dy < BOARD_SIZE:
                        line = [board[i + k * dx][j + k * dy] for k in range(5)]
                        stone_count = sum(1 for p in line if p == color)
                        if stone_count == 5:
                            score += WEIGHTS["five"]
                        elif stone_count == 4 and EMPTY in line:
                            score += WEIGHTS["open_four"]
                        elif stone_count == 3 and line.count(EMPTY) == 2:
                            score += WEIGHTS["open_three"]
                        elif stone_count == 2 and line.count(EMPTY) == 3:
                            score += WEIGHTS["open_two"]
    return score


def is_game_over(board):
    """
    检查游戏是否结束，即是否有一方获胜
    """
    for color in [BLACK, WHITE]:
        if evaluate_position(board, color) >= WEIGHTS["five"]:
            return True
    return False


def alpha_beta_search(board, depth, alpha, beta, maximizing_player):
    """
    使用Alpha-Beta剪枝进行博弈树搜索
    """
    if depth == 0 or is_game_over(board):
        return evaluate_position(board, AI_COLOR) - evaluate_position(board, PLAYER_COLOR)

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
        board[i][j] = EMPTY
        if score > best_score:
            best_score = score
            best_move = move
    if best_move:
        i, j = best_move
        board[i][j] = AI_COLOR


def print_board():
    """
    打印棋盘状态
    """
    print('   ', end='')
    for j in range(BOARD_SIZE):
        print(f'{j:2}', end=' ')
    print()
    for i in range(BOARD_SIZE):
        print(f'{i:2} ', end=' ')
        for j in range(BOARD_SIZE):
            if board[i][j] == BLACK:
                print(" X", end=" ")
            elif board[i][j] == WHITE:
                print(" O", end=" ")
            else:
                print(" .", end=" ")
        print()


if __name__ == '__main__':
    ROUND = PLAYER_ROUND  # 人机对弈，人先手
    while True:
        print_board()
        if ROUND == PLAYER_ROUND:  # 用户下棋回合
            x = int(input("请输入行坐标（0-14）："))
            y = int(input("请输入列坐标（0-14）："))
            board[x][y] = PLAYER_COLOR
            ROUND = AI_ROUND  # 用户下棋后，轮到AI下棋
        elif ROUND == AI_ROUND:  # AI下棋回合
            start = time.time()
            make_ai_move()
            end = time.time()
            print("AI考虑时间：", end - start, "秒")
            ROUND = PLAYER_ROUND  # AI下棋后，轮到用户下棋

        if is_game_over(board):  # 检查游戏是否结束
            print_board()
            print("游戏结束")
            break