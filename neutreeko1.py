import pickle
from collections import deque


# 盤面boardを表示する
def print_board(board):
    black,white,b_turn = board      # タプルboardの中身をblack,white,b_turnに入れる
    for y in range(5):
        for x in range(5):
            if (x,y) in white:      # (x,y)というタプルがwhiteの要素なら
                print('W', end=' ')
            elif (x,y) in black:    # (x,y)というタプルがblackの要素なら
                print('B', end=' ')
            else:                   # それ以外なら
                print('.', end=' ')
        if y==4:
            print("[Black]" if b_turn else "[White]") # 現在の手番
        else:
            print()

# 8方向のベクトルの集合
dir = ( (-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1) )

# boardの次の盤面リストを返す
def next(board):
    black,white,b_turn = board         # b_turnがTrueなら現在の手番は黒
    moves = black if b_turn else white # 動かすコマ群を選択し，
    moves = list(moves)                # リストにしておく
    next_list = []
    for _ in range(3):     # 3回繰り返す
        x,y = moves.pop(0) # movesの先頭要素を取り出しx,yにセットする(2番目3番目は残す)
        for dx,dy in dir:  # 8方向それぞれについて繰り返す
            dest = None    # 移動先がある場合，以下のwhileループで移動先がセットされる
            # (tx,ty)が盤面内にあり，かつ他のコマと衝突しない限り(dx,dy)ずつ移動させる
            tx,ty = x+dx, y+dy            
            while 0<=tx<=4 and 0<=ty<=4 and (not (tx,ty) in black) and (not (tx,ty) in white):
                dest = (tx,ty)
                tx,ty = tx+dx, ty+dy
            if dest != None: # 最初の位置から移動できるなら
                moves_new = [dest, moves[0], moves[1]] # 小さい順に並んでないので
                moves_new = tuple(sorted(moves_new))   # ソートしてからタプルにする
                next_board = (moves_new,white,False) if b_turn else (black,moves_new,True)
                next_list.append(next_board)
        moves.append((x,y)) # 先頭は動かしたので末尾にまわす
    return next_list

# 手番ではない側のコマが縦横斜めに3つ並んでいたらTrueを返す
# Trueとなる場合，
# ひとつ前の手番が動かした結果，ひとつ前の手番側が3つ並んだということなので，
# ひとつ前の手番側の勝ち，現在の手番側の負け
def end(board):
    black,white,b_turn = board
    test = white if b_turn else black
    t0,t1,t2 = test # t0,t1,t2はソートされているのでt0は最も左、t2は最も右
    if t0==(0,0) and t1==(1,0) and t2==(2,0):
        return True
    else:
        return False
    #### 本当は横・斜め・縦に並んでいたらTrueを返すようにする
    #### ソートされていることを利用するとコンパクトに判別できる

# 到達可能な全ての盤面を訪問し，全てのall_boards[]に0または-1を格納する
# ぴょんぴょんしょうぎはvisit()で再帰を使って深さ優先探索したが，
# ここではキューを使って幅優先探索をしてみる
def find_zero():
    q = deque() # 訪問対象の盤面を入れるキュー(FIFO)
    q.append(initial_board)
    all_boards[initial_board] = -2
    count = 0
    while len(q) > 0:                   # キューに残っている限り続ける
        board = q.popleft()             # キューから1つ取り出し，以下で0か-1に決める
        if end(board):
            all_boards[board] = 0       # 3つ並んでいる盤面なので0(手番の負け)にする
        else:
            all_boards[board] = -1      # 3つ並んでいない盤面は-1(深さ不明)にする
            next_list = next(board)     # 次の盤面リストを作成し，
            for b in next_list:         # そのそれぞれについて
                if not b in all_boards: # キューに入れられたことがなければ
                    q.append(b)         # キューに入れる
                    all_boards[b] = -2  # キューに入れたので-2にしておく ifではじかれる
        count += 1                      # (キューに入れるのは1回でよい)
        if count & 0xffff ==0: print('zero', len(q), len(all_boards))

# 深さwin_depth(奇数)の勝ち盤面を探す
def find_win(win_depth):
    count = 0
    wins = 0
    for board,depth in all_boards.items(): # 全ての到達可能盤面とその深さを1つずつ取り出す
        if depth == -1:
            next_list = next(board) # boardは自番の，next_boardsは相手番の盤面
            ####
            #### next_list内のどれかが負け盤面ならboardの勝ち(その手で相手の負け)
            #### all_boards[board] = win_depth で登録し，
            #### win += 1                      を行う
            ####
        count += 1
        if count & 0xffff == 0: print('win', win_depth, count, wins)#経過表示
    return wins

# 深さlose_depth(偶数)の負け盤面を探す
def find_lose(lose_depth):
    count = 0
    loses = 0
    for board,depth in all_boards.items(): # 全ての到達可能盤面とその深さを1つずつ取り出す
        if depth == -1:
            next_list = next(board) # boardは自番の，next_boardsは相手番の盤面
            ####
            #### next_list内の全てが勝ち盤面ならboardの負け(何をしても相手の勝ち)
            #### all_boards[board] = lose_depth で登録し，
            #### loses += 1                     を行う
            ####
            #### next_list内に深さ不明か，あるいは相手の負け盤面があれば
            #### boardは負けではない
            ####
        count += 1
        if count & 0xffff == 0: print('lose', lose_depth, count, loses)#経過表示
    return loses

# 全ての盤面を格納する辞書
# キーは盤面，値は深さ(終了するまでに必要な手数)
# find_zero()実行中にキューに入れた盤面は一時的に-2になる(再訪問させないため)
# find_zero()終了時には全ての盤面が格納され，値は0(手番の負け)か-1(深さ不明)になる
all_boards = {}
    
# $ python neutreeko1.py により以下が実行される
if __name__ == "__main__":
    # 初期盤面
    black = ((1,0), (3,0), (2,3))
    white = ((2,1), (1,4), (3,4))
    black = tuple(sorted(black)) # コマの位置は
    white = tuple(sorted(white)) # ソートしておく
    initial_board = (black, white, True)  # 先手は黒
    print(initial_board)
    print_board(initial_board)
    
    # 初期盤面の次の盤面
    list2 = next(initial_board)
    print(len(list2))  # 14個ある
    for b in list2:
        print(b)
        print_board(b)
    
    # 全ての盤面を訪問しall_boardsに格納する　勝敗の決した盤面の深さは0に，それ以外は-1にする
    find_zero()
    print('len(all_boards) =', len(all_boards)) # 7079992と表示されるが正しくは6935248
    
    #### find_win(1)
    #### find_lose(2)
    #### # 以下，新たに見つかる盤面数が0でない限り継続する

    # all_boardsの中身をall_boards.pickleというファイルに保存する
    with open('all_boards.pickle', 'wb') as file:
        pickle.dump(all_boards, file)