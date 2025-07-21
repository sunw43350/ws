# market_ws_collector/config.py

# ✅ 标准化符号配置（使用统一格式，如 BTC-USDT）
DEFAULT_SYMBOLS = {
    "ascendex": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "krakenfutures":    ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "binance":  ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "ADA-USDT"],
    "bitmex":   ["BTC-USDT", "ETH-USDT", "XRP-USDT"]
    # 后续交易所可继续添加
}

# ✅ 每个交易所的 WebSocket 接入地址
WS_ENDPOINTS = {
    "ascendex": "wss://ascendex.com/1/api/pro/v2/stream",
    "krakenfutures":   "wss://beta-ws.kraken.com/v2",
    "binance":  "wss://stream.binance.com:9443/ws",
    "bitmex":   "wss://www.bitmex.com/realtime"
    # 更多交易所陆续补充
}


