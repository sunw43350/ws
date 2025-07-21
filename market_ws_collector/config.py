# market_ws_collector/config.py

# ✅ 标准化符号配置（使用统一格式，如 BTC-USDT）
DEFAULT_SYMBOLS = {
    "ascendex": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "krakenfutures":    ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"],
    "bingx": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

}

# ✅ 每个交易所的 WebSocket 接入地址
WS_ENDPOINTS = {
    "ascendex": "wss://ascendex.com/1/api/pro/v2/stream",
    "krakenfutures":   "wss://futures.kraken.com/ws/v1",
    "bingx": "wss://open-api-ws.bingx.com/market"

}

DEFAULT_SYMBOLS.update({
    "bitfinex": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]

})

WS_ENDPOINTS.update({
    "bitfinex": "wss://api-pub.bitfinex.com/ws/2"
})


DEFAULT_SYMBOLS.update({
    "bitget": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LTCUSDT"]
})

WS_ENDPOINTS.update({
    "bitget": "wss://ws.bitget.com/v2/ws/public"
})

DEFAULT_SYMBOLS.update({
    "bitmart": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "LTCUSDT"]
})

WS_ENDPOINTS.update({
    "bitmart": "wss://openapi-ws-v2.bitmart.com/api?protocol=1.1"
})

DEFAULT_SYMBOLS.update({
    "bitmex": ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD", "LTCUSD"]
})

WS_ENDPOINTS.update({
    "bitmex": "wss://ws.bitmex.com/realtime"
})

DEFAULT_SYMBOLS.update({
    "bitrue": ["btcusdt", "ethusdt", "solusdt", "xrpusdt", "ltcusdt"]
})

WS_ENDPOINTS.update({
    "bitrue": "wss://ws.bitrue.com/kline-api/ws"
})
