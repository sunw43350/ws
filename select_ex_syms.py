import pickle

exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))

# for ex, syms in sorted(exchange_symbols.items(), key=lambda x: len(x[1]), reverse=True):
#     print(ex, len(syms))


# 获取所有 symbol 列表
all_symbols = sorted({symbol for syms in exchange_symbols.values() for symbol in syms})

# 打印表头
print("exchange," + ",".join(all_symbols))

# 打印每个交易所对应的 symbol 行
for ex in sorted(exchange_symbols.keys()):
    row = [str(int(symbol in exchange_symbols[ex])) for symbol in all_symbols]
    print(f"{ex}," + ",".join(row))