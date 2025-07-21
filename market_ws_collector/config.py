# market_ws_collector/config.py

DEFAULT_SYMBOLS = {
    "ascendex": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "binance": ["BTC-USDT", "ETH-USDT"],
    "krakenfutures": ["BTC-PERP", "ETH-PERP"],
    "bitmex": ["BTC-USDT", "ETH-USDT"]
    # 其他交易所陆续添加
}


WS_ENDPOINTS = {
    "ascendex": "wss://ascendex.com/1/api/pro/v2/stream",
    "binance": "wss://stream.binance.com:9443/ws",
    "bitmex": "wss://www.bitmex.com/realtime"
    # 后续交易所可继续添加
}
