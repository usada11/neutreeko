import pickle
import time
from collections import deque


# --- board representation helpers ---
# map (x,y) (0<=x,y<=4) to index 0..24
def pos_to_idx(pos):
    x,y = pos
    return y*5 + x

def idx_to_pos(idx):
    x = idx % 5
    y = idx // 5
    return (x,y)

def mask_from_positions(positions):
    m = 0
    for p in positions:
        m |= 1 << pos_to_idx(p)
    return m

def positions_from_mask(m):
    res=[]
    for i in range(25):
        if (m>>i)&1:
            res.append(idx_to_pos(i))
    return tuple(sorted(res))

def sorted_positions_tuple(positions):
    return tuple(sorted(positions))

# 8 directions (dx,dy)
DIRS = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

# generate next boards from a given board
# board: (black_mask, white_mask, b_turn_bool)
def next_boards(board):
    black_mask, white_mask, b_turn = board
    pieces = []
    if b_turn:
        # generate list of black piece indices (sorted)
        for i in range(25):
            if (black_mask>>i)&1:
                pieces.append(i)
    else:
        for i in range(25):
            if (white_mask>>i)&1:
                pieces.append(i)
    # ensure list ordering like original (we will rotate: first, second, third)
    pieces = list(pieces)
    res=[]
    for k in range(3):
        i = pieces.pop(0)
        x0,y0 = idx_to_pos(i)
        for dx,dy in DIRS:
            tx,ty = x0+dx, y0+dy
            dest = None
            while 0<=tx<5 and 0<=ty<5:
                idx = ty*5 + tx
                if ((black_mask>>idx)&1) or ((white_mask>>idx)&1):
                    break
                dest = idx
                tx += dx; ty += dy
            if dest is not None:
                # build new mask: move piece i -> dest
                if b_turn:
                    new_black = black_mask & ~(1<<i)
                    new_black |= 1<<dest
                    new_white = white_mask
                    nb = (new_black, new_white, False)
                else:
                    new_white = white_mask & ~(1<<i)
                    new_white |= 1<<dest
                    new_black = black_mask
                    nb = (new_black, new_white, True)
                res.append(nb)
        pieces.append(i)
    return res

# end check: if the side NOT to move has three-in-a-row (aligned)
# return True if board is terminal (i.e., current player has already lost)
def is_end(board):
    black_mask, white_mask, b_turn = board
    test_mask = white_mask if b_turn else black_mask
    # get the three positions (there are exactly 3 bits)
    idxs = [i for i in range(25) if (test_mask>>i)&1]
    if len(idxs) != 3:
        return False
    (x0,y0),(x1,y1),(x2,y2) = (idx_to_pos(idxs[0]), idx_to_pos(idxs[1]), idx_to_pos(idxs[2]))
    dx1,dy1 = x1-x0, y1-y0
    dx2,dy2 = x2-x1, y2-y1
    return (dx1,dy1) in DIRS and (dx2,dy2) == (dx1,dy1)

# pretty print board
def print_board(board):
    black_mask, white_mask, b_turn = board
    for y in range(5):
        row=''
        for x in range(5):
            i = y*5 + x
            if (white_mask>>i)&1:
                row += 'W '
            elif (black_mask>>i)&1:
                row += 'B '
            else:
                row += '. '
        row += "[Black]" if b_turn else "[White]"
        print(row)
    print()

# --- main solver logic ---
def enumerate_reachable(initial_board, progress_interval=500000):
    all_boards = {}
    q = deque([initial_board])
    all_boards[initial_board] = -2  # -2 means in-queue marker
    count = 0
    t0 = time.time()
    while q:
        b = q.popleft()
        if is_end(b):
            all_boards[b] = 0
        else:
            all_boards[b] = -1  # unknown depth for now
            for nb in next_boards(b):
                if nb not in all_boards:
                    all_boards[nb] = -2
                    q.append(nb)
        count += 1
        if count % progress_interval == 0:
            print("enumerated", count, "queue", len(q), "total", len(all_boards), "time", time.time()-t0)
    print("enumeration done: total boards =", len(all_boards), "time", time.time()-t0)
    return all_boards

def retrograde_solve(all_boards):
    # all_boards: dict board->value (0 for terminal loss for side to move, -1 for unknown)
    depth = 1
    t0 = time.time()
    changed_total = 0
    while True:
        changes = 0
        if depth % 2 == 1:
            # odd depth: boards from which there exists a move to a 0 (opponent loss) are wins for player to move
            for board,val in list(all_boards.items()):
                if val == -1:
                    for nb in next_boards(board):
                        if all_boards.get(nb) == 0:
                            all_boards[board] = depth
                            changes += 1
                            break
        else:
            # even depth: boards where ALL moves lead to opponent win (i.e., nexts all have odd depth < depth)
            for board,val in list(all_boards.items()):
                if val == -1:
                    nexts = next_boards(board)
                    if not nexts:
                        continue
                    all_opponent_win = True
                    for nb in nexts:
                        v = all_boards.get(nb)
                        # opponent win means v is odd (opponent wins in odd plies)
                        if v == -1 or v == -2 or (v % 2 == 0):
                            all_opponent_win = False
                            break
                    if all_opponent_win:
                        all_boards[board] = depth
                        changes += 1
        print("depth", depth, "found", changes, "boards; elapsed", time.time()-t0)
        if changes == 0:
            break
        depth += 1
        changed_total += changes
    # after propagation, we may still have -1 boards (cyclic/drawish). treat them as 'unknown/draw' if any.
    return all_boards

def analyze_results(all_boards, initial_board):
    # find value for initial board
    val = all_boards.get(initial_board, None)
    # find max depth boards
    max_depth = -999
    max_boards = []
    for b,v in all_boards.items():
        if v >= 0 and v > max_depth:
            max_depth = v
            max_boards = [(b,v)]
        elif v == max_depth:
            max_boards.append((b,v))
    return val, max_depth, max_boards

# --- top-level driver ---
def solve_and_report(initial_black_positions, initial_white_positions, label):
    black_mask = mask_from_positions(initial_black_positions)
    white_mask = mask_from_positions(initial_white_positions)
    initial_board = (black_mask, white_mask, True)  # black to move (先手は黒)
    print("=== Start:", label)
    print("Initial board:")
    print_board(initial_board)

    pickle_name = f"allboards_{label}.pickle"
    try:
        print("Trying to load existing pickle:", pickle_name)
        with open(pickle_name,'rb') as f:
            all_boards = pickle.load(f)
        print("Loaded pickle, boards:", len(all_boards))
    except Exception as e:
        print("No pickle found or load failed (", e, "). Enumerating reachable boards ...")
        all_boards = enumerate_reachable(initial_board)
        print("Saving pickle to", pickle_name)
        with open(pickle_name,'wb') as f:
            pickle.dump(all_boards,f,protocol=4)

    print("Retrograde solving ... (this may take time)")
    all_boards = retrograde_solve(all_boards)

    val, max_depth, max_boards = analyze_results(all_boards, initial_board)
    print("=== Results for", label)
    if val is None:
        print("Initial board not in reachable set (unexpected).")
    else:
        if val == 0:
            print("Initial board: LOSS for side to move (Black) (0 plies).")
        elif val == -1:
            print("Initial board: unknown/draw (no solved value).")
        else:
            # val positive -> win/lose depending parity: odd => current player wins in val plies,
            # even => current player loses in val plies
            if val % 2 == 1:
                print(f"Initial board: WIN for player to move (Black) in {val} plies (half-moves).")
            else:
                print(f"Initial board: LOSE for player to move (Black) in {val} plies.")
    print("Board(s) requiring the most plies to finish: depth =", max_depth)
    for b,v in max_boards[:10]:
        black_mask, white_mask, bturn = b
        print("Black:", positions_from_mask(black_mask), "White:", positions_from_mask(white_mask), "turn:", "Black" if bturn else "White")
    # save final solved all_boards
    with open(pickle_name,'wb') as f:
        pickle.dump(all_boards,f,protocol=4)
    print("Saved final all_boards to", pickle_name)
    print()

# --- the three given positions ---
if __name__ == "__main__":
    # (1)
    b1 = tuple(sorted(((1,0), (4,0), (2,2))))
    w1 = tuple(sorted(((1,2), (0,3), (3,4))))
    # (2)
    b2 = tuple(sorted(((1,0), (4,1), (1,3))))
    w2 = tuple(sorted(((3,0), (0,2), (1,4))))
    # (3) neutreeko initial
    b3 = tuple(sorted(((1,0), (3,0), (2,3))))
    w3 = tuple(sorted(((2,1), (1,4), (3,4))))

    solve_and_report(b1,w1,"case1")
    solve_and_report(b2,w2,"case2")
    solve_and_report(b3,w3,"case3")
