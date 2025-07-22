import pickle
from config import SELECT_EXCHANGES

# 加载数据
exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# 只保留选中的交易所
filtered_exchanges = [ex for ex in SELECT_EXCHANGES if ex in exchange_symbols]

# 获取所有 symbol
all_symbols = sorted(symbol_exchanges.keys())

# 构建矩阵并统计每个 symbol 在选中交易所中出现的次数
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

# 按 count 降序排列
sorted_data = sorted(zip(all_symbols, counts, matrix), key=lambda x: x[1], reverse=True)

# 输出 Markdown 表格
header = "| symbol | count | " + " | ".join(filtered_exchanges) + " |"
separator = "|" + " --- |" * (len(filtered_exchanges) + 2)
print(header)
print(separator)

for symbol, count, row in sorted_data:
    print("| " + symbol + " | " + str(count) + " | " + " | ".join(row) + " |")
