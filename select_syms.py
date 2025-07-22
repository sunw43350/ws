import pickle
import csv
from config import SELECT_EXCHANGES

# 加载数据
exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# 筛选要统计的交易所
filtered_exchanges = [ex for ex in SELECT_EXCHANGES if ex in exchange_symbols]

# 所有 symbol
all_symbols = sorted(symbol_exchanges.keys())

# 保存 count > 10 的 symbol 数据
filtered_symbol_data = []
exchange_contract_counter = {ex: 0 for ex in filtered_exchanges}
exchange_contract_symbols = {ex: [] for ex in filtered_exchanges}

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
            exchange_contract_symbols[ex].append(symbol)

# 写入 count > 10 的 symbol 列表
with open("symbols_with_count_gt10.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["symbol", "count", "exchanges"])
    for symbol, count, exchanges in filtered_symbol_data:
        writer.writerow([symbol, count, ", ".join(exchanges)])

# 写入每个交易所支持的热门 symbol 统计
with open("exchange_contract_counts.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["exchange", "supported_contracts_count"])
    for ex in sorted(filtered_exchanges, key=lambda x: exchange_contract_counter[x], reverse=True):
        writer.writerow([ex, exchange_contract_counter[ex]])

# ✅ 写入每个交易所支持的 symbol 具体内容
with open("exchange_contract_counts_with_symbols.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["exchange", "supported_contracts_count", "symbols"])
    for ex in sorted(filtered_exchanges, key=lambda x: exchange_contract_counter[x], reverse=True):
        symbols = exchange_contract_symbols[ex]
        writer.writerow([ex, exchange_contract_counter[ex], ", ".join(symbols)])
