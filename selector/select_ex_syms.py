import pickle

exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# 过滤 symbol 数量小于 100 的 exchange
filtered_exchanges = [ex for ex, syms in exchange_symbols.items() if len(syms) >= 5]
filtered_exchanges = sorted(filtered_exchanges)



# 获取所有 symbol
all_symbols = sorted(symbol_exchanges.keys())

# 构建矩阵并统计每个 symbol 出现的交易所个数
matrix = []
counts = []
for symbol in all_symbols:
    row = []
    count = 0
    for exchange in filtered_exchanges:
        if symbol in exchange_symbols[exchange]:
            row.append("1")
            count += 1
        else:
            row.append("")
    matrix.append(row)
    counts.append(count)

# 按个数降序排列
sorted_data = sorted(zip(all_symbols, counts, matrix), key=lambda x: x[1], reverse=True)

# 打印 Markdown 表头
header = "| symbol | count | " + " | ".join(filtered_exchanges) + " |"
separator = "|" + " --- |" * (len(filtered_exchanges) + 2)
print(header)
print(separator)

# 打印每行
for symbol, count, row in sorted_data:
    print("| " + symbol + " | " + str(count) + " | " + " | ".join(row) + " |")