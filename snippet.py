t1 = ((1,2), (3,4), (5,6))
t2 = ((1,2), (3,4), (5,6))
t3 = ((1,2), (3,4), (1,0))
print(t1 == t2) # True
print(t1 == t3) # False
print()

# タプルをソートする場合，一度リストに変換してから行う
print(                  t3   ) # ((1, 2), (3, 4), (1, 0))
print(             list(t3)  ) # [(1, 2), (3, 4), (1, 0)] リストに変換(要素はタプル)
print(      sorted(list(t3)) ) # [(1, 0), (1, 2), (3, 4)] リストにするとソートできる
print(tuple(sorted(list(t3)))) # ((1, 0), (1, 2), (3, 4)) タプルに戻す
print()

# 盤面のタプルも比較できる
b1 = ( ((1,0), (2,3), (3,0)), ((1,4), (2,1), (3,4)), True  )
b2 = ( ((1,0), (2,3), (3,0)), ((1,4), (2,1), (3,4)), True  ) # 同じ盤面
b3 = ( ((0,1), (1,0), (3,0)), ((1,4), (2,1), (3,4)), False ) # 異なる盤面
print(b1 == b2) # True
print(b1 == b3) # False
print()

# タプルやリストの要素はin演算子で調べることができる
print((1,2) in t1)     # True
print((7,8) in t1)     # False
print(not (7,8) in t1) # True
print()

# 辞書の全ての要素をループで処理する方法
d={}
d["one"] = 100
d["two"] = 200
for k,v in d.items():
    print(k,v)       # one 100
print()              # two 200 と表示される

# 辞書のキーの存在テスト
print("one" in d)    # True
print("ten" in d)    # False
print()

# タプルを辞書のキーにすることができる
d2 = {}
d2[b1] = 5
d2[b3] = 6
print(d2[b1])        # 5
print(b1 in d2)      # True
print(b2 in d2)      # True
print(b3 in d2)      # True