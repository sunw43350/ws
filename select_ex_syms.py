import pickle

exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# for ex, syms in sorted(exchange_symbols.items(), key=lambda x: len(x[1]), reverse=True):
#     print(ex, len(syms))


# 过滤 symbol 数量小于 100 的 exchange
filtered_exchanges = [ex for ex, syms in exchange_symbols.items() if len(syms) >= 100]
filtered_exchanges = sorted(filtered_exchanges)

# 获取所有 symbol
all_symbols = sorted(symbol_exchanges.keys())

# 构建矩阵：行是 symbol，列是 exchange
matrix = []
for symbol in all_symbols:
    row = []
    for exchange in filtered_exchanges:
        row.append(1 if symbol in exchange_symbols[exchange] else 0)
    matrix.append(row)

# 打印表头
print("symbol," + ",".join(filtered_exchanges))
# 打印每行
for symbol, row in zip(all_symbols, matrix):
    print(symbol + "," + ",".join(map(str, row)))