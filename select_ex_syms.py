import pickle

exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# for ex, syms in sorted(exchange_symbols.items(), key=lambda x: len(x[1]), reverse=True):
#     print(ex, len(syms))


# 获取所有交易所和所有symbol
exchanges = list(exchange_symbols.keys())
all_symbols = sorted({symbol for syms in exchange_symbols.values() for symbol in syms})

# 构建矩阵
matrix = []
for ex in exchanges:
    row = [1 if symbol in exchange_symbols[ex] else 0 for symbol in all_symbols]
    matrix.append(row)

# 打印表头
print("exchange,", ",".join(all_symbols))
# 打印每一行
for ex, row in zip(exchanges, matrix):
    print(f"{ex}," + ",".join(map(str, row)))