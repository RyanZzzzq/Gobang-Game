"""
-*- coding: utf-8 -*-
Desc: 智能五子棋
Auth: Zhou Ziqi
GitHub: RyanZzzzq
Requirement: 使用python语言，结合博弈树启发式搜索和alpha-beta剪枝技术，开发一个五子棋博弈游戏。
Plus:   1. 设计一个15行15列棋盘，要求自行给出估价函数，按极大极小搜索方法，并采用α-β剪枝技术；
        2. 采用人机对弈方式，对弈双方设置不同颜色的棋子，一方走完一步后，等待对方走步，对弈过程的每个棋局都在屏幕上显示出来；
        3. 当某一方在横、竖或斜方向上先有5个棋子连成一线时，该方为赢。
PS: 能力有限:( ，只编写玩家执黑先下情况，且忽略禁手问题
Version: v2.0
Updates: 1. 增加GUI界面，用户选择落子位置方式改为鼠标点击，对弈过程更直观易读；
         2. 保持原有AI智能程度，难度适中，测试中暂未出现无厘头的落子情况。
"""

import tkinter as tk
import tkinter.messagebox
import numpy as np

# 棋盘大小
BOARD_SIZE = 15

# 定义棋盘状态
EMPTY = 0
BLACK = 1
WHITE = 2

# 定义评估函数中的权重
# 根据五子棋中连珠情况，给出权重
WEIGHTS = {
    "open_two": 10,       # 活二
    "half_three": 100,    # 死三
    "open_three": 1000,   # 活三
    "half_four": 10000,   # 死四
    "open_four": 100000,  # 活四
    "five": 1000000       # 五连
}

# 定义搜索深度
MAX_DEPTH = 3

# 定义搜索方向，包括水平、垂直和对角线
DIRECTIONS = [(1, 0), (0, 1), (1, 1), (1, -1)]

# 初始化棋盘
board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

# 用户执黑，AI执白
PLAYER_COLOR = BLACK
AI_COLOR = WHITE

# 定义棋局状态
PLAYER_ROUND = 1
AI_ROUND = 2

# 定义棋子的半径
RADIUS = 15

# 定义棋盘的边距
PADDING = 20

# 定义棋盘格子的大小
GRID_SIZE = 30

# 创建窗口
window = tk.Tk()
window.title('五子棋')

# 创建棋盘
canvas = tk.Canvas(window, width=PADDING*2+GRID_SIZE*(BOARD_SIZE-1), height=PADDING*2+GRID_SIZE*(BOARD_SIZE-1),
                   bg="#CDBA96")
canvas.pack()

# 绘制棋盘格线
for board_i in range(BOARD_SIZE):
    canvas.create_line(PADDING, PADDING + board_i * GRID_SIZE, PADDING + (BOARD_SIZE - 1) * GRID_SIZE,
                       PADDING + board_i * GRID_SIZE)
    canvas.create_line(PADDING + board_i * GRID_SIZE, PADDING, PADDING + board_i * GRID_SIZE,
                       PADDING + (BOARD_SIZE - 1) * GRID_SIZE)


def get_valid_moves(game_board):
    """
    获取当前棋局的合法移动位置
    """
    moves = set()
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if game_board[i][j] != EMPTY:
                # 检查此棋子周围的位置
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        ni, nj = i + di, j + dj
                        if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE and game_board[ni][nj] == EMPTY:
                            moves.add((ni, nj))
    return list(moves)


def evaluate_position(game_board, color):
    """
    评估当前棋局的得分
    """
    score = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if game_board[i][j] == color:
                for dx, dy in DIRECTIONS:
                    if 0 <= i + 4 * dx < BOARD_SIZE and 0 <= j + 4 * dy < BOARD_SIZE:
                        line = [game_board[i + k * dx][j + k * dy] for k in range(5)]
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


def is_game_over(game_board):
    """
    检查游戏是否结束，即是否有一方获胜
    返回获胜方的颜色，如果没有人获胜则返回 None
    """
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if game_board[i][j] != EMPTY:
                for direction in DIRECTIONS:
                    dx, dy = direction
                    x, y = i, j
                    count = 0
                    while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE:
                        if game_board[x][y] == game_board[i][j]:
                            count += 1
                            if count == 5:
                                return game_board[i][j]
                        else:
                            count = 0
                        x += dx
                        y += dy
    return None


def alpha_beta_search(game_board, depth, alpha, beta, maximizing_player):
    """
    使用Alpha-Beta剪枝进行博弈树搜索
    """
    if depth == 0 or is_game_over(game_board):
        return evaluate_position(game_board, AI_COLOR) - evaluate_position(game_board, PLAYER_COLOR)

    valid_moves = get_valid_moves(game_board)
    if maximizing_player:
        max_eval = float('-inf')
        for move in valid_moves:
            i, j = move
            game_board[i][j] = AI_COLOR
            evaluation = alpha_beta_search(game_board, depth - 1, alpha, beta, False)
            game_board[i][j] = EMPTY
            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            i, j = move
            game_board[i][j] = PLAYER_COLOR
            evaluation = alpha_beta_search(game_board, depth - 1, alpha, beta, True)
            game_board[i][j] = EMPTY
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return min_eval


def make_ai_move():
    """
    AI进行移动，使用Alpha-Beta剪枝搜索选择最佳位置
    """
    window.update_idletasks()
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
        canvas.create_oval(PADDING+j*GRID_SIZE-RADIUS, PADDING+i*GRID_SIZE-RADIUS,
                           PADDING+j*GRID_SIZE+RADIUS, PADDING+i*GRID_SIZE+RADIUS, fill="white")
    window.update()


def click(event):
    """
    鼠标点击事件
    """
    global board
    i, j = round((event.y - PADDING) / GRID_SIZE), round((event.x - PADDING) / GRID_SIZE)
    if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE and board[i][j] == EMPTY:
        board[i][j] = PLAYER_COLOR
        canvas.create_oval(PADDING+j*GRID_SIZE-RADIUS, PADDING+i*GRID_SIZE-RADIUS, PADDING+j*GRID_SIZE+RADIUS,
                           PADDING+i*GRID_SIZE+RADIUS, fill="black")
        if is_game_over(board):
            tk.messagebox.showinfo("游戏结束", "你赢了！")  # 根据游戏结果用户获胜显示对应信息
            window.quit()
        else:
            make_ai_move()
            if is_game_over(board):
                tk.messagebox.showinfo("游戏结束", "AI赢了！")  # 根据游戏结果AI获胜显示对应信息
                window.quit()


# 绑定鼠标点击事件
canvas.bind("<Button-1>", click)

if __name__ == "__main__":
    window.mainloop()  # 进入主循环
