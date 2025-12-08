import pickle
from collections import deque


# 盤面表示
def print_board(board):
    black,white,b_turn = board
    for y in range(5):
        for x in range(5):
            if (x,y) in white:
                print('W', end=' ')
            elif (x,y) in black:
                print('B', end=' ')
            else:
                print('.', end=' ')
        if y==4:
            print("[Black]" if b_turn else "[White]")
        else:
            print()

# 8方向
dir = ((-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1))

# 3つの石が一直線に並んでいるか判定
def is_line(p0, p1, p2):
    return (p1[0]-p0[0] == p2[0]-p1[0]) and (p1[1]-p0[1] == p2[1]-p1[1])

# 終局判定
def end(board):
    black, white, b_turn = board
    test = white if b_turn else black
    t0, t1, t2 = test
    return is_line(t0,t1,t2)

# 次の盤面を生成
def next(board):
    black,white,b_turn = board
    moves = list(black if b_turn else white)
    next_list = []
    for _ in range(3):
        x,y = moves.pop(0)
        for dx,dy in dir:
            dest=None
            tx,ty=x+dx,y+dy
            while 0<=tx<=4 and 0<=ty<=4 and ((tx,ty) not in black) and ((tx,ty) not in white):
                dest=(tx,ty)
                tx+=dx; ty+=dy
            if dest != None:
                mv = [dest, moves[0], moves[1]]
                mv = tuple(sorted(mv))
                nb = (mv, white, False) if b_turn else (black, mv, True)
                next_list.append(nb)
        moves.append((x,y))
    return next_list

# 全盤面を列挙（0 = 終局負け盤面, -1 = 未確定）
def find_zero():
    q = deque()
    q.append(initial_board)
    all_boards[initial_board] = -2
    while q:
        bd = q.popleft()
        if end(bd):
            all_boards[bd] = 0
        else:
            all_boards[bd] = -1
            for nb in next(bd):
                if nb not in all_boards:
                    q.append(nb)
                    all_boards[nb] = -2

# 深さ win_depth（奇数）の勝ち盤面を探索
def find_win(win_depth):
    found = 0
    for bd, depth in list(all_boards.items()):
        if depth == -1:  # 未確定
            for nxt in next(bd):
                if all_boards[nxt] == win_depth - 1:  # 相手が負け
                    all_boards[bd] = win_depth
                    found += 1
                    break
    return found

# 深さ lose_depth（偶数）の負け盤面を探索
def find_lose(lose_depth):
    found = 0
    for bd, depth in list(all_boards.items()):
        if depth == -1:
            nxts = next(bd)
            # 全ての次盤面が相手の勝ちなら負け
            if all(all_boards[nxt] == lose_depth - 1 for nxt in nxts):
                all_boards[bd] = lose_depth
                found += 1
    return found

#---------------------------------------------

# 初期盤面（課題どおり）
black_init = ((1,0),(3,0),(2,3))
white_init = ((2,1),(1,4),(3,4))
black_init = tuple(sorted(black_init))
white_init = tuple(sorted(white_init))

initial_board = (black_init, white_init, True)

all_boards = {}

if __name__ == "__main__":
    print("Initial:")
    print_board(initial_board)
    
    # 0: 終局負け盤面
    find_zero()
    print("Total reachable =", len(all_boards))

    # 深さ 1,2,3... を交互に探索
    depth = 1
    while True:
        if depth % 2 == 1:
            c = find_win(depth)
        else:
            c = find_lose(depth)
        print(f"depth {depth}: {c} found")
        if c == 0:
            break
        depth += 1

    # ファイル保存
    with open("all_boards.pickle", "wb") as f:
        pickle.dump(all_boards, f)

    print("Saved all_boards.pickle")
