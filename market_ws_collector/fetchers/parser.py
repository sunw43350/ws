def parse_binance(data):
    symbols = []
    for item in data.get("symbols", []):
        symbols.append(item.get("symbol"))
    return symbols

# 可继续添加其他交易所的解析方法
