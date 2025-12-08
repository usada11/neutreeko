import pickle

with open("all_boards.pickle", "rb") as f:
    boards = pickle.load(f)

print("Type:", type(boards))
print("Count:", len(boards))

# 例: 先頭だけチェック
for i, b in enumerate(boards):
    print(b)
    if i >= 3:
        break
