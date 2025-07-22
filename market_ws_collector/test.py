import pickle
import csv

basedir = '../assets/'  # ✅ 统一指定存储目录

# 加载数据
exchange_symbols = pickle.load(open(f'{basedir}/filtered_exchange_symbols_gt50.pkl', 'rb'))

print(f"✅ 成功加载 {len(exchange_symbols)} 个交易所的 symbol 数据")

for exchange, symbols in exchange_symbols.items():
    print(f"{exchange} 支持的 symbol 数量: {len(symbols)}")
    print(f"示例 symbols: {', '.join(symbols[:50])} ...")  # 打印前5个示  例