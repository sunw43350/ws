import pickle
import csv

basedir = '../assets/'  # ✅ 统一指定存储目录

# 加载数据
exchange_symbols = pickle.load(open(f'{basedir}/filtered_exchange_symbols_gt50.pkl', 'rb'))

print(f"✅ 成功加载 {len(exchange_symbols)} 个交易所的 symbol 数据")

# for exchange, symbols in exchange_symbols.items():
#     print(f"{exchange} 支持的 symbol 数量: {len(symbols)}")
#     print(f"示例 symbols: {', '.join(symbols[:50])} ...")  # 打印前5个示  例


exchange_symbols_gt50 = exchange_symbols

# 获取所有交易所和 symbol 集合
exchange_list = sorted(exchange_symbols_gt50.keys())
symbol_exchange_map = {}

for ex, symbols in exchange_symbols_gt50.items():
    for sym in symbols:
        symbol_exchange_map.setdefault(sym, set()).add(ex)

# 对每个 symbol 统计支持它的交易所个数
symbol_counts = [(sym, len(exchanges)) for sym, exchanges in symbol_exchange_map.items()]

# 排序并获取前 100 个 symbol（按被支持的交易所数目降序）
top_100_symbols = sorted(symbol_counts, key=lambda x: x[1], reverse=True)[:100]

# 构建矩阵数据
matrix_data = []
for symbol, count in top_100_symbols:
    row = [symbol, str(count)]
    for ex in exchange_list:
        row.append("1" if ex in symbol_exchange_map[symbol] else "")
    matrix_data.append(row)

# 输出为 CSV 文件
with open("top100_symbol_exchange_matrix.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    header = ["symbol", "count"] + exchange_list
    writer.writerow(header)
    for row in matrix_data:
        writer.writerow(row)

print("✅ 已保存前 100 个合约与支持交易所的矩阵到 top100_symbol_exchange_matrix.csv")
