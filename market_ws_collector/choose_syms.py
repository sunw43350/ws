import pickle
import csv

basedir = '../assets/'

# 加载数据
with open(f'{basedir}/filtered_exchange_symbols_gt50.pkl', 'rb') as f:
    exchange_symbols_gt50 = pickle.load(f)

# 获取所有交易所列表
exchange_list = sorted(exchange_symbols_gt50.keys())

# 构建 symbol -> set(exchange) 映射
symbol_exchange_map = {}
for exchange, symbols in exchange_symbols_gt50.items():
    for symbol in symbols:
        symbol_exchange_map.setdefault(symbol, set()).add(exchange)

# 统计每个 symbol 被多少个交易所支持
symbol_counts = [(symbol, len(exchanges)) for symbol, exchanges in symbol_exchange_map.items()]

# 取支持交易所数量最多的前 100 个 symbol
top_100_symbols = sorted(symbol_counts, key=lambda x: x[1], reverse=True)[:100]

# 统一格式转换：'SAND/USDT:USDT' → 'SAND-USDT'
def normalize_symbol(symbol: str) -> str:
    if ':' in symbol:
        symbol = symbol.split(':')[0]
    return symbol.replace('/', '-')

# 构建 CSV 行数据
matrix_data = []
for symbol, count in top_100_symbols:
    norm_symbol = normalize_symbol(symbol)
    row = [norm_symbol, str(count)]
    for ex in exchange_list:
        row.append("1" if ex in symbol_exchange_map[symbol] else "")
    matrix_data.append(row)

# 输出 CSV 文件
csv_path = f'{basedir}/top100_symbol_exchange_matrix.csv'
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "count"] + exchange_list)
    writer.writerows(matrix_data)

print(f"✅ 已保存 top100 矩阵到 {csv_path}")
