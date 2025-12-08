import pickle
import random

from neutreeko1 import print_board

# 全盤面の深さデータを読み込む
with open('all_boards.pickle', 'rb') as file:
    all_boards = pickle.load(file)
    
    # 到達可能な盤面数
    reachable = len(all_boards)
    print(reachable)
    
    # 深さが3の盤面をランダムに表示
    count = 0
    for board,depth in all_boards.items():
        if depth == 3 and random.random() < 0.01:
            print(depth, board)
            print_board(board)
            count += 1
            if count == 3: # 大量にあるので3個表示したら終えることにする
                break
    
    # 深さごとの盤面数
    # all_boardsの要素(キーboard,値depth)について，
    # depth==dとなる要素数を合計してnに入れ，それを表示する
    s = 0
    for d in range(100):
        n = sum(depth == d for board,depth in all_boards.items())
        print(f'{d:>2} {n:>8}')
        s += n
        if n==0:
            break

    # 引き分けとなる盤面数
    draw = reachable - s
    print(draw)
