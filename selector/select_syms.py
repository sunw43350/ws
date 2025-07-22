import pickle
import json
from config import SELECT_EXCHANGES

basedir = '../assets/'  # ✅ 统一指定存储目录

# 加载数据
exchange_symbols = pickle.load(open(f'{basedir}/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open(f'{basedir}/symbol_exchanges.pkl', 'rb'))

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
    if count > 10 and count < 20:
        filtered_symbol_data.append({
            "symbol": symbol,
            "count": count,
            "exchanges": present_exchanges
        })
        for ex in present_exchanges:
            exchange_contract_counter[ex] += 1
            exchange_contract_symbols[ex].append(symbol)

# ✅ 写入 count > 10 的 symbol 列表到 JSON
with open("symbols_with_count_gt10.json", "w", encoding="utf-8") as f:
    json.dump(filtered_symbol_data, f, ensure_ascii=False, indent=2)

# ✅ 写入每个交易所支持的 symbol 数量到 JSON
exchange_counts_json = [
    {"exchange": ex, "supported_contracts_count": exchange_contract_counter[ex]}
    for ex in sorted(filtered_exchanges, key=lambda x: exchange_contract_counter[x], reverse=True)
]
with open("exchange_contract_counts.json", "w", encoding="utf-8") as f:
    json.dump(exchange_counts_json, f, ensure_ascii=False, indent=2)

# ✅ 写入每个交易所支持的 symbol 详细数据
exchange_contract_details = []
exchange_symbols_gt50 = {}

for ex in sorted(filtered_exchanges, key=lambda x: exchange_contract_counter[x], reverse=True):
    symbol_list = exchange_contract_symbols[ex]
    exchange_contract_details.append({
        "exchange": ex,
        "supported_contracts_count": exchange_contract_counter[ex],
        "symbols": symbol_list
    })
    if exchange_contract_counter[ex] > 50:
        exchange_symbols_gt50[ex] = symbol_list

with open("exchange_contract_counts_with_symbols.json", "w", encoding="utf-8") as f:
    json.dump(exchange_contract_details, f, ensure_ascii=False, indent=2)

# ✅ 保存符合条件的交易所 + symbols 到 assets 路径
with open(f"filtered_exchange_symbols_gt50.json", "w", encoding="utf-8") as f:
    json.dump(exchange_symbols_gt50, f, ensure_ascii=False, indent=2)

print(f"✅ 已保存 {len(exchange_symbols_gt50)} 个交易所到 {basedir}/filtered_exchange_symbols_gt50.json")


######################################## ✅ 选取前 100 个交易所支持的 symbol
# ✅ 选取 filtered_symbol_data 中前 100 个 symbol，构建 {exchange: [symbols]} 格式
top_100_symbols = filtered_symbol_data[:20]
top_100_exchange_symbols = {}

def normalize_symbol(symbol: str) -> str:
    """将原始合约格式统一为 'BASE-QUOTE'，如 BTC/USDT:USDT → BTC-USDT"""
    try:
        base_quote = symbol.split(":")[0]  # "BTC/USDT"
        base, quote = base_quote.split("/")
        return f"{base}-{quote}"
    except Exception as e:
        print(f"❌ symbol 格式异常: {symbol} → {e}")
        return symbol  # fallback: 返回原始 symbol

for entry in top_100_symbols:
    raw_symbol = entry["symbol"]
    symbol = normalize_symbol(raw_symbol)  # ✅ 格式标准化
    for ex in entry["exchanges"]:
        top_100_exchange_symbols.setdefault(ex, []).append(symbol)

# ✅ 收集要删除的交易所
to_delete = []

for ex in top_100_exchange_symbols:
    num = len(top_100_exchange_symbols[ex])
    print(f"交易所 {ex} 支持的前 100 个 symbol 数量: {num}")
    if num < 2:
        to_delete.append(ex)
        print(f"⚠️ 警告: 交易所 {ex} 支持的前 100 个 symbol 数量少于 5 个！")

# ✅ 统一删除
for ex in to_delete:
    del top_100_exchange_symbols[ex]

# ✅ 保存到 JSON 文件
with open("top100_exchange_symbols.json", "w", encoding="utf-8") as f:
    json.dump(top_100_exchange_symbols, f, ensure_ascii=False, indent=2)

print(f"✅ 已保存前 100 个 symbol 的交易所分布到 top100_exchange_symbols.json")

