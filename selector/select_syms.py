import pickle
import json

basedir = '../assets/'

# 加载原始 pickle 数据
with open(f'{basedir}/exchange_symbols.pkl', 'rb') as f:
    exchange_symbols = pickle.load(f)

with open(f'{basedir}/symbol_exchanges.pkl', 'rb') as f:
    symbol_exchanges = pickle.load(f)

# 写入为 JSON 文件
with open(f'{basedir}/exchange_symbols.json', 'w', encoding='utf-8') as f:
    json.dump(exchange_symbols, f, ensure_ascii=False, indent=2)

with open(f'{basedir}/symbol_exchanges.json', 'w', encoding='utf-8') as f:
    json.dump(symbol_exchanges, f, ensure_ascii=False, indent=2)

print("✅ 原始 pickle 数据已成功转换为 JSON 格式并保存。")
