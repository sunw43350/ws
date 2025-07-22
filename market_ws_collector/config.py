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
    "bitrue": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "bitrue": "wss://ws.bitrue.com/kline-api/ws"
})

DEFAULT_SYMBOLS.update({
    "blofin": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "blofin": "wss://openapi.blofin.com/ws/public"
})

DEFAULT_SYMBOLS.update({
    "bybit": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LINK-USDT", "ADA-USDT"]
})

WS_ENDPOINTS.update({
    "bybit": "wss://stream.bybit.com/v5/public/linear"
})

DEFAULT_SYMBOLS.update({
    "coinbase": ["BTC-USD", "ETH-USD", "SOL-USD", "LTC-USD", "ADA-USD"]
})

WS_ENDPOINTS.update({
    "coinbase": "wss://advanced-trade-ws.coinbase.com"
})

DEFAULT_SYMBOLS.update({
    "coinbase": ["BTC-USD", "ETH-USD", "SOL-USD", "LTC-USD", "ADA-USD"]
})

WS_ENDPOINTS.update({
    "coinbase": "wss://advanced-trade-ws.coinbase.com"
})

DEFAULT_SYMBOLS.update({
    "cryptocom": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "cryptocom": "wss://stream.crypto.com/exchange/v1/market"
})


DEFAULT_SYMBOLS.update({
    "digifinex": ["BTC-USDT", "ETH-USDT"]
})

WS_ENDPOINTS.update({
    "digifinex": "wss://openapi.digifinex.com/swap_ws/v2/"
})


DEFAULT_SYMBOLS.update({
    "gateio": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "gateio": "wss://fx-ws.gateio.ws/v4/ws/usdt"
})

DEFAULT_SYMBOLS.update({
    "huobi": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT", "XRP-USDT"]
})

WS_ENDPOINTS.update({
    "huobi": "wss://api.huobi.pro/ws"
})


DEFAULT_SYMBOLS.update({
    "lbank": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "LTC-USDT", "XRP-USDT"]
})

WS_ENDPOINTS.update({
    "lbank": "wss://www.lbkex.net/ws/V2/"
})

DEFAULT_SYMBOLS.update({
    "mexc": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "mexc": "wss://contract.mexc.com/edge"
})


DEFAULT_SYMBOLS.update({
    "okx": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "okx": "wss://ws.okx.com:8443/ws/v5/public"
})


DEFAULT_SYMBOLS.update({
    "oxfun": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "oxfun": "wss://api.ox.fun/v2/websocket"
})

DEFAULT_SYMBOLS.update({
    "phemex": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "LTC-USDT"]
})

WS_ENDPOINTS.update({
    "phemex": "wss://ws.phemex.com"
})
