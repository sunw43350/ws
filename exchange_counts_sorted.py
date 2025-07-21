import pickle

exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))

# 统计每个交易所的合约数量
exchange_counts = [(ex, len(syms)) for ex, syms in exchange_symbols.items()]

# 按数量降序排列
exchange_counts_sorted = sorted(exchange_counts, key=lambda x: x[1], reverse=True)

# 打印 Markdown 表格
print("| exchange | symbol_count |")
print("| --- | --- |")
for ex, count in exchange_counts_sorted:
    print(f"| {ex} | {count} |")