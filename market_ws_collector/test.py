import pickle
import csv
from config import SELECT_EXCHANGES

basedir = '../assets/'  # ✅ 统一指定存储目录

# 加载数据
exchange_symbols = pickle.load(open(f'{basedir}/filtered_exchange_symbols_gt50.pkl', 'rb'))

print(f"✅ 成功加载 {len(exchange_symbols)} 个交易所的 symbol 数据")