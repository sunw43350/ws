import pickle
import csv
from config import SELECT_EXCHANGES

# 加载数据
exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# 筛选在 SELECT_EXCHANGES 中的交易所
filtered_exchanges = [ex for ex in SELECT_EXCHANGES if ex in exchange_symbols]

# 所有 symbol
all_symbols = sorted(symbol_exchanges.keys())

# 统计每个 symbol 在哪些交易所出现，并计算 count
filtered_symbol_data = []  # 用于后续写入 CSV
exchange_contract_counter = {ex: 0 for ex in filtered_exchanges}  # 每个交易所支持的合约数

for symbol in all_symbols:
    present_exchanges = []
    for exchange in filtered_exchanges:
        if symbol in exchange_symbols[exchange]:
            present_exchanges.append(exchange)
    count = len(present_exchanges)
    if count > 10:
        filtered_symbol_data.append((symbol, count, present_exchanges))
        for ex in present_exchanges:
            exchange_contract_counter[ex] += 1

# 写入 count > 10 的 symbol 数据
with open("symbols_with_count_gt10.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "count", "exchanges"])
    for symbol, count, exchanges in filtered_symbol_data:
        writer.writerow([symbol, count, ", ".join(exchanges)])

# 写入交易所支持的合约数统计
with open("exchange_contract_counts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["exchange", "supported_contracts_count"])
    for ex, cnt in sorted(exchange_contract_counter.items(), key=lambda x: x[1], reverse=True):
        writer.writerow([ex, cnt])
